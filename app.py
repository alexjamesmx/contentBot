import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from src.generation.story_generator import StoryGenerator
from src.generation.tts_generator import TTSGenerator
from src.generation.tts_elevenlabs import ElevenLabsTTS
from src.generation.subtitle_generator import SubtitleGenerator
from src.generation.video_composer import VideoComposer
from src.generation.story_templates import STORY_TEMPLATES, list_genres
from src.utils.config import (
    GROQ_API_KEY, ELEVENLABS_API_KEY,
    BACKGROUNDS_DIR, FONTS_DIR, PENDING_DIR,
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    STORY_TEMPERATURE, STORY_MAX_TOKENS, PROJECT_ROOT
)
from src.utils.metadata import VideoMetadata

app = Flask(__name__)
CORS(app)

# Story library directory
STORIES_DIR = PROJECT_ROOT / "output" / "stories"
STORIES_DIR.mkdir(parents=True, exist_ok=True)

# Progress tracking for video generation
video_progress = {}

# ==================== CONFIG ENDPOINTS ====================

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    backgrounds = [f.name for f in BACKGROUNDS_DIR.glob("*.mp4")]
    fonts = [f.name for f in FONTS_DIR.glob("*.ttf")] + [f.name for f in FONTS_DIR.glob("*.otf")]

    return jsonify({
        'success': True,
        'config': {
            'api_keys': {
                'groq': bool(GROQ_API_KEY),
                'elevenlabs': bool(ELEVENLABS_API_KEY)
            },
            'video': {
                'width': VIDEO_WIDTH,
                'height': VIDEO_HEIGHT,
                'fps': VIDEO_FPS
            },
            'story': {
                'temperature': STORY_TEMPERATURE,
                'max_tokens': STORY_MAX_TOKENS
            },
            'assets': {
                'backgrounds': backgrounds,
                'fonts': fonts
            },
            'genres': list_genres()
        }
    })

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration (save to .env)"""
    data = request.json

    # Update .env file
    env_path = Path('.env')
    env_lines = []

    if env_path.exists():
        with open(env_path, 'r') as f:
            env_lines = f.readlines()

    # Update specific keys
    updated_keys = set()
    for i, line in enumerate(env_lines):
        for key, value in data.items():
            if line.startswith(f"{key}="):
                env_lines[i] = f"{key}={value}\n"
                updated_keys.add(key)

    # Add new keys
    for key, value in data.items():
        if key not in updated_keys:
            env_lines.append(f"{key}={value}\n")

    # Save
    with open(env_path, 'w') as f:
        f.writelines(env_lines)

    return jsonify({'success': True, 'message': 'Configuration updated'})

# ==================== TEMPLATE ENDPOINTS ====================

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all story templates"""
    return jsonify({
        'success': True,
        'templates': STORY_TEMPLATES
    })

@app.route('/api/templates/<genre>', methods=['GET'])
def get_template(genre):
    """Get specific template"""
    if genre not in STORY_TEMPLATES:
        return jsonify({'success': False, 'error': 'Genre not found'}), 404

    return jsonify({
        'success': True,
        'template': STORY_TEMPLATES[genre]
    })

@app.route('/api/templates/<genre>', methods=['PUT'])
def update_template(genre):
    """Update story template"""
    data = request.json

    if genre not in STORY_TEMPLATES:
        return jsonify({'success': False, 'error': 'Genre not found'}), 404

    # Update template
    STORY_TEMPLATES[genre].update(data)

    # Save to file
    templates_path = Path('src/generation/story_templates.py')
    # TODO: Implement safe template file update

    return jsonify({'success': True, 'message': 'Template updated'})

# ==================== GENERATION ENDPOINTS ====================

@app.route('/api/generate/story', methods=['POST'])
def generate_story():
    """Generate a story"""
    data = request.json
    genre = data.get('genre', 'comedy')
    custom_prompt = data.get('custom_prompt', None)
    target_duration = data.get('target_duration', 60)

    try:
        story_gen = StoryGenerator()

        if custom_prompt:
            story = story_gen.generate_story(genre=genre, custom_prompt=custom_prompt, target_duration=target_duration)
        else:
            story = story_gen.generate_story(genre=genre, target_duration=target_duration)

        # Validate
        is_valid, issues = story_gen.validate_story(story)

        return jsonify({
            'success': True,
            'story': story,
            'validation': {
                'is_valid': is_valid,
                'issues': issues
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate/audio', methods=['POST'])
def generate_audio():
    """Generate TTS audio"""
    data = request.json
    text = data.get('text')
    voice = data.get('voice', 'default')
    use_elevenlabs = data.get('use_elevenlabs', bool(ELEVENLABS_API_KEY))

    if not text:
        return jsonify({'success': False, 'error': 'Text is required'}), 400

    try:
        # Generate unique filename based on text hash
        audio_hash = abs(hash(text))
        output_path = PENDING_DIR / f"audio_{audio_hash}.mp3"

        if use_elevenlabs and ELEVENLABS_API_KEY:
            tts = ElevenLabsTTS(ELEVENLABS_API_KEY)
            audio_path = tts.generate_audio(text, voice=voice, output_path=str(output_path))

            # Get duration
            temp_tts = TTSGenerator()
            duration = temp_tts.get_audio_duration(audio_path)
        else:
            tts = TTSGenerator()
            audio_path = tts.generate_audio(text, output_path=str(output_path))
            duration = tts.get_audio_duration(audio_path)

        return jsonify({
            'success': True,
            'audio_path': str(audio_path),
            'duration': duration
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate/subtitles', methods=['POST'])
def generate_subtitles():
    """Generate subtitles"""
    data = request.json
    text = data.get('text')
    duration = data.get('duration')
    words_per_chunk = data.get('words_per_chunk', 2)

    if not text or not duration:
        return jsonify({'success': False, 'error': 'Text and duration required'}), 400

    try:
        sub_gen = SubtitleGenerator(words_per_chunk=words_per_chunk)
        subtitles = sub_gen.generate_subtitles(text, duration)

        return jsonify({
            'success': True,
            'subtitles': [{'start': s, 'end': e, 'text': t} for s, e, t in subtitles]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate/video/progress/<video_id>', methods=['GET'])
def get_video_progress(video_id):
    """Get progress of video generation"""
    progress = video_progress.get(video_id, {'progress': 0, 'status': 'Not started'})
    return jsonify(progress)

@app.route('/api/generate/video', methods=['POST'])
def generate_video():
    """Generate complete video"""
    data = request.json

    # Extract parameters
    story_text = data.get('story_text')
    genre = data.get('genre', 'comedy')
    audio_path = data.get('audio_path')
    subtitles = data.get('subtitles')
    background_video = data.get('background_video')

    if not story_text or not audio_path:
        return jsonify({'success': False, 'error': 'Story text and audio required'}), 400

    # Generate video ID for progress tracking
    video_id = str(abs(hash(story_text)))
    video_progress[video_id] = {'progress': 0, 'status': 'Starting...'}

    try:
        video_progress[video_id] = {'progress': 5, 'status': 'Preparing...'}
        print(f"\n[VIDEO] Starting video generation (ID: {video_id})...")
        print(f"[VIDEO] Genre: {genre}")
        print(f"[VIDEO] Story length: {len(story_text)} chars")
        print(f"[VIDEO] Subtitle count: {len(subtitles)}")
        print(f"[VIDEO] Background: {background_video or 'random'}")

        # Convert subtitles back to tuples
        subtitle_tuples = [(s['start'], s['end'], s['text']) for s in subtitles]
        print(f"[VIDEO] Converted {len(subtitle_tuples)} subtitles")
        video_progress[video_id] = {'progress': 10, 'status': 'Loading background...'}

        # Construct full audio path if only filename provided
        if not os.path.isabs(audio_path):
            audio_path = str(PENDING_DIR / audio_path)

        print(f"[VIDEO] Using audio path: {audio_path}")
        print(f"[VIDEO] Audio file exists: {os.path.exists(audio_path)}")

        if not os.path.exists(audio_path):
            error_msg = f"Audio file not found at: {audio_path}"
            print(f"[VIDEO] ERROR: {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 400

        # Create video
        composer = VideoComposer()
        output_path = PENDING_DIR / f"{genre}_{hash(story_text)}.mp4"
        print(f"[VIDEO] Output path: {output_path}")

        if background_video:
            bg_path = BACKGROUNDS_DIR / background_video
            print(f"[VIDEO] Using background: {bg_path}")
            if not bg_path.exists():
                print(f"[VIDEO] WARNING: Background video not found, using random")
                bg_path = None
        else:
            bg_path = None
            print(f"[VIDEO] Using random background")

        print(f"[VIDEO] Calling video composer...")
        video_progress[video_id] = {'progress': 20, 'status': 'Starting render...'}

        # Progress callback that updates the global progress dict
        def update_progress(progress, status):
            # Map 0-100% rendering progress to 20-90% overall progress
            overall_progress = 20 + int(progress * 0.7)
            video_progress[video_id] = {'progress': overall_progress, 'status': status}

        video_path = composer.create_video(
            audio_path=audio_path,
            subtitles=subtitle_tuples,
            output_path=str(output_path),
            story_metadata={'story': story_text, 'genre': genre},
            genre=genre,
            background_video=str(bg_path) if bg_path else None,
            progress_callback=update_progress
        )
        print(f"[VIDEO] Video created: {video_path}")
        video_progress[video_id] = {'progress': 90, 'status': 'Generating metadata...'}

        # Generate metadata
        print(f"[VIDEO] Generating metadata...")
        meta_gen = VideoMetadata()
        metadata = meta_gen.create_metadata_json(
            video_path=video_path,
            story={'story': story_text, 'genre': genre},
            audio_path=audio_path,
            subtitle_path='',
            genre=genre
        )
        print(f"[VIDEO] Metadata generated")
        video_progress[video_id] = {'progress': 100, 'status': 'Complete!'}

        print(f"[VIDEO] SUCCESS! Video ready at: {video_path}\n")

        # Clean up progress after a delay
        import threading
        def cleanup():
            import time
            time.sleep(10)
            video_progress.pop(video_id, None)
        threading.Thread(target=cleanup, daemon=True).start()

        return jsonify({
            'success': True,
            'video_id': video_id,
            'video_path': str(video_path),
            'metadata': metadata
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[VIDEO] ERROR: {str(e)}")
        print(f"[VIDEO] Traceback:\n{error_trace}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== FILE MANAGEMENT ====================

@app.route('/api/files/backgrounds', methods=['GET'])
def get_backgrounds():
    """List background videos"""
    backgrounds = []
    for f in BACKGROUNDS_DIR.glob("*.mp4"):
        stat = f.stat()
        backgrounds.append({
            'name': f.name,
            'size': stat.st_size,
            'modified': stat.st_mtime
        })

    return jsonify({'success': True, 'backgrounds': backgrounds})

@app.route('/api/files/backgrounds', methods=['POST'])
def upload_background():
    """Upload background video"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    # Save file
    filepath = BACKGROUNDS_DIR / file.filename
    file.save(str(filepath))

    return jsonify({'success': True, 'message': 'Background uploaded', 'filename': file.filename})

@app.route('/api/files/backgrounds/<filename>', methods=['DELETE'])
def delete_background(filename):
    """Delete background video"""
    filepath = BACKGROUNDS_DIR / filename

    if not filepath.exists():
        return jsonify({'success': False, 'error': 'File not found'}), 404

    filepath.unlink()
    return jsonify({'success': True, 'message': 'Background deleted'})

@app.route('/api/files/videos', methods=['GET'])
def get_videos():
    """List generated videos"""
    videos = []
    for f in PENDING_DIR.glob("*.mp4"):
        stat = f.stat()

        # Try to load metadata
        metadata_path = f.with_suffix('.json')
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, 'r') as mf:
                metadata = json.load(mf)

        videos.append({
            'name': f.name,
            'path': str(f),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'metadata': metadata
        })

    videos.sort(key=lambda x: x['modified'], reverse=True)

    return jsonify({'success': True, 'videos': videos})

@app.route('/api/files/video/<filename>', methods=['GET'])
def serve_video(filename):
    """Serve video file with proper streaming headers"""
    response = send_from_directory(
        PENDING_DIR,
        filename,
        mimetype='video/mp4',
        as_attachment=False
    )
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.route('/api/files/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve audio file"""
    return send_from_directory(PENDING_DIR, filename, mimetype='audio/mpeg')

@app.route('/api/files/background/<filename>', methods=['GET'])
def serve_background(filename):
    """Serve background video file"""
    return send_from_directory(BACKGROUNDS_DIR, filename, mimetype='video/mp4')

# ==================== STORY LIBRARY ====================

@app.route('/api/stories', methods=['GET'])
def get_stories():
    """Get all saved stories"""
    stories = []
    for f in STORIES_DIR.glob("*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                story_data = json.load(file)
                story_data['id'] = f.stem
                story_data['filename'] = f.name
                stories.append(story_data)
        except Exception as e:
            print(f"Error loading story {f}: {e}")

    # Sort by modified date (newest first)
    stories.sort(key=lambda x: x.get('created_at', 0), reverse=True)
    return jsonify({'success': True, 'stories': stories})

@app.route('/api/stories', methods=['POST'])
def save_story():
    """Save a story to the library"""
    data = request.json
    story_text = data.get('story')
    genre = data.get('genre', 'custom')
    title = data.get('title', 'Untitled Story')

    if not story_text:
        return jsonify({'success': False, 'error': 'Story text required'}), 400

    # Generate ID from timestamp
    import time
    story_id = f"story_{int(time.time())}"

    story_data = {
        'id': story_id,
        'title': title,
        'story': story_text,
        'genre': genre,
        'word_count': len(story_text.split()),
        'created_at': time.time(),
        'updated_at': time.time()
    }

    # Save to file
    filepath = STORIES_DIR / f"{story_id}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(story_data, f, indent=2, ensure_ascii=False)

    return jsonify({'success': True, 'story': story_data})

@app.route('/api/stories/<story_id>', methods=['GET'])
def get_story(story_id):
    """Get a specific story"""
    filepath = STORIES_DIR / f"{story_id}.json"

    if not filepath.exists():
        return jsonify({'success': False, 'error': 'Story not found'}), 404

    with open(filepath, 'r', encoding='utf-8') as f:
        story_data = json.load(f)

    return jsonify({'success': True, 'story': story_data})

@app.route('/api/stories/<story_id>', methods=['PUT'])
def update_story(story_id):
    """Update an existing story"""
    filepath = STORIES_DIR / f"{story_id}.json"

    if not filepath.exists():
        return jsonify({'success': False, 'error': 'Story not found'}), 404

    # Load existing story
    with open(filepath, 'r', encoding='utf-8') as f:
        story_data = json.load(f)

    # Update with new data
    data = request.json
    import time

    if 'story' in data:
        story_data['story'] = data['story']
        story_data['word_count'] = len(data['story'].split())
    if 'title' in data:
        story_data['title'] = data['title']
    if 'genre' in data:
        story_data['genre'] = data['genre']

    story_data['updated_at'] = time.time()

    # Save
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(story_data, f, indent=2, ensure_ascii=False)

    return jsonify({'success': True, 'story': story_data})

@app.route('/api/stories/<story_id>', methods=['DELETE'])
def delete_story(story_id):
    """Delete a story"""
    filepath = STORIES_DIR / f"{story_id}.json"

    if not filepath.exists():
        return jsonify({'success': False, 'error': 'Story not found'}), 404

    filepath.unlink()
    return jsonify({'success': True, 'message': 'Story deleted'})

# ==================== VIDEO UPLOAD ====================

@app.route('/api/upload/video', methods=['POST'])
def upload_video():
    """Upload a source video for processing"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    # Create uploads directory
    uploads_dir = PROJECT_ROOT / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    import time
    timestamp = int(time.time())
    ext = Path(file.filename).suffix
    filename = f"upload_{timestamp}{ext}"
    filepath = uploads_dir / filename
    file.save(str(filepath))

    return jsonify({
        'success': True,
        'message': 'Video uploaded',
        'filename': filename,
        'path': str(filepath)
    })

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'version': '2.0.0-mvp'
    })

if __name__ == '__main__':
    print("=== ContentBot MVP Backend Starting ===")
    print(f"Backgrounds: {BACKGROUNDS_DIR}")
    print(f"Output: {PENDING_DIR}")
    print(f"Stories: {STORIES_DIR}")
    print(f"Groq API: {'OK' if GROQ_API_KEY else 'MISSING'}")
    print(f"ElevenLabs API: {'OK' if ELEVENLABS_API_KEY else 'MISSING'}")
    print()
    print("Backend running at: http://localhost:5000")
    print("Frontend: cd contentbot-ui && npm run dev")
    print()

    app.run(debug=True, port=5000, host='0.0.0.0')
