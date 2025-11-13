"""ContentBot UI - Flask Backend API"""
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
    STORY_TEMPERATURE, STORY_MAX_TOKENS
)
from src.utils.metadata import VideoMetadata

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

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

    try:
        story_gen = StoryGenerator()

        if custom_prompt:
            # Use custom prompt
            story = story_gen.generate_story(genre=genre)  # TODO: Add custom prompt support
        else:
            story = story_gen.generate_story(genre=genre)

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
        output_path = PENDING_DIR / f"temp_audio_{hash(text)}.mp3"

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

    try:
        print(f"\n[VIDEO] Starting video generation...")
        print(f"[VIDEO] Genre: {genre}")
        print(f"[VIDEO] Story length: {len(story_text)} chars")
        print(f"[VIDEO] Subtitle count: {len(subtitles)}")
        print(f"[VIDEO] Background: {background_video or 'random'}")

        # Convert subtitles back to tuples
        subtitle_tuples = [(s['start'], s['end'], s['text']) for s in subtitles]
        print(f"[VIDEO] Converted {len(subtitle_tuples)} subtitles")

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
        video_path = composer.create_video(
            audio_path=audio_path,
            subtitles=subtitle_tuples,
            output_path=str(output_path),
            story_metadata={'story': story_text, 'genre': genre},
            genre=genre,
            background_video=str(bg_path) if bg_path else None
        )
        print(f"[VIDEO] Video created: {video_path}")

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

        print(f"[VIDEO] SUCCESS! Video ready at: {video_path}\n")
        return jsonify({
            'success': True,
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
    """Serve video file"""
    return send_from_directory(PENDING_DIR, filename, mimetype='video/mp4')

@app.route('/api/files/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve audio file"""
    return send_from_directory(PENDING_DIR, filename, mimetype='audio/mpeg')

@app.route('/api/files/background/<filename>', methods=['GET'])
def serve_background(filename):
    """Serve background video file"""
    return send_from_directory(BACKGROUNDS_DIR, filename, mimetype='video/mp4')

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("=== ContentBot UI Backend Starting ===")
    print(f"Backgrounds: {BACKGROUNDS_DIR}")
    print(f"Output: {PENDING_DIR}")
    print(f"Groq API: {'OK' if GROQ_API_KEY else 'MISSING'}")
    print(f"ElevenLabs API: {'OK' if ELEVENLABS_API_KEY else 'MISSING'}")
    print()
    print("Backend running at: http://localhost:5000")
    print("Frontend: cd contentbot-ui && npm run dev")
    print()

    app.run(debug=True, port=5000, host='0.0.0.0')
