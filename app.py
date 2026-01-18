import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from src.generation.story_generator import StoryGenerator
from src.generation.story_context_manager import StoryContextManager
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
from src.utils.job_tracker import (
    create_job, get_job, update_job, delete_job,
    list_active_jobs, list_user_jobs,
    JobStatus, JobType
)

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


# ==================== GENERATION ENDPOINTS ====================

@app.route('/api/generate/story', methods=['POST'])
def generate_story():
    """Generate a story with job tracking (creates series with total_parts=1)"""
    data = request.json
    genre = data.get('genre', 'comedy')
    custom_prompt = data.get('custom_prompt', None)
    target_duration = data.get('target_duration', 60)

    # Create job
    import time
    job_id = f"story_{int(time.time() * 1000)}"
    job = create_job(job_id, JobType.STORY, metadata={'genre': genre, 'target_duration': target_duration})

    try:
        update_job(job_id, status=JobStatus.RUNNING, progress=10)

        # Create series with total_parts=1 (unified model)
        manager = StoryContextManager()
        series_result = manager.create_series(
            genre=genre,
            total_parts=1,
            theme=custom_prompt or "Single video",
            base_prompt=custom_prompt
        )
        series_id = series_result['story_id']

        update_job(job_id, progress=30, metadata={'series_id': series_id})

        # Generate first (only) part
        story_result = manager.generate_next_part(series_id, target_duration)

        update_job(job_id, progress=70)

        # Generate AI title
        ai_title = manager.generate_ai_title(series_id)

        update_job(job_id, progress=80)

        # Validate
        story_gen = StoryGenerator()
        story = {
            'story': story_result['story_text'],
            'hook': story_result['part_metadata'].get('hook', ''),
            'word_count': story_result['part_metadata']['word_count'],
            'estimated_duration': story_result['duration']
        }
        is_valid, issues = story_gen.validate_story(story)

        # Mark complete
        update_job(job_id, status=JobStatus.COMPLETED, progress=100, result=story)

        return jsonify({
            'success': True,
            'job_id': job_id,
            'series_id': series_id,
            'part_number': 1,
            'title': ai_title or 'Untitled',  # ✅ ADD: Include AI-generated title
            'story': story,
            'validation': {
                'is_valid': is_valid,
                'issues': issues
            }
        })
    except Exception as e:
        update_job(job_id, status=JobStatus.FAILED, error=str(e))
        return jsonify({'success': False, 'error': str(e), 'job_id': job_id}), 500

@app.route('/api/stories/improve', methods=['POST'])
def improve_story():
    """Improve existing story using AI (not regeneration)"""
    data = request.json
    current_text = data.get('current_text')
    improvement_type = data.get('improvement_type', 'enhance')
    custom_instructions = data.get('custom_instructions', '').strip()
    genre = data.get('genre', 'comedy')
    target_duration = data.get('target_duration', 75)
    series_id = data.get('series_id')
    part_number = data.get('part_number', 1)

    if not current_text:
        return jsonify({'success': False, 'error': 'current_text is required'}), 400

    # If custom instructions provided, use them instead of predefined types
    if custom_instructions:
        improvement_type = 'custom'
    else:
        valid_types = ['enhance', 'expand', 'refine', 'make_viral']
        if improvement_type not in valid_types:
            return jsonify({'success': False, 'error': f'improvement_type must be one of: {", ".join(valid_types)}'}), 400

    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        # Build improvement prompt based on type
        improvement_prompts = {
            'custom': f"""Improve this story based on the following custom instructions:

{custom_instructions}

Original Story:
{current_text}

Requirements:
- Follow the custom instructions exactly
- Maintain the story format
- Return ONLY the improved story text, no explanations or meta-commentary
- Keep it suitable for TikTok/YouTube Shorts""",

            'enhance': f"""Make this story more engaging and dramatic while keeping the EXACT same storyline and key events.

Original Story:
{current_text}

Requirements:
- Keep the same plot, characters, and events
- Make it more emotionally engaging
- Add dramatic pauses and emphasis
- Improve word choice for impact
- Target: {target_duration} seconds (~{int(target_duration * 2.5)} words)
- Maintain TikTok/Shorts viral style

Return ONLY the improved story text, no explanations.""",

            'expand': f"""Expand this story with more details and context to reach the target duration.

Original Story:
{current_text}

Requirements:
- Add vivid details and sensory descriptions
- Expand emotional moments
- Add context where needed
- Keep the same storyline
- Target: {target_duration} seconds (~{int(target_duration * 2.5)} words)
- Must be {int(target_duration * 2.5)} words or more for monetization

Return ONLY the expanded story text, no explanations.""",

            'refine': f"""Refine this story by improving grammar, pacing, and hooks.

Original Story:
{current_text}

Requirements:
- Fix any grammar or flow issues
- Improve sentence pacing (vary length)
- Strengthen the hook (first sentence)
- Make the ending more impactful
- Keep the same length (~{len(current_text.split())} words)
- Maintain viral TikTok/Shorts style

Return ONLY the refined story text, no explanations.""",

            'make_viral': f"""Optimize this story for maximum TikTok/Shorts virality.

Original Story:
{current_text}

Requirements:
- Add a powerful hook in the first 3 seconds
- Insert micro-hooks every 10-15 seconds to maintain retention
- Add emotional tension and conflict
- Create a cliffhanger or impactful ending
- Use viral phrases and patterns
- Target: {target_duration} seconds (~{int(target_duration * 2.5)} words)
- Optimize for comments and shares

Return ONLY the viral-optimized story text, no explanations."""
        }

        system_prompt = f"""You are an expert TikTok/YouTube Shorts storytelling AI specializing in viral content optimization.

Genre: {genre}
Style: Fast-paced, engaging, optimized for retention
Goal: Improve the story without changing the core narrative

Rules:
- NEVER add meta-commentary or explanations
- Return ONLY the story text
- Maintain natural, human-like language (avoid AI detection)
- Keep sentences punchy and varied in length
- Use emotional language and emphasis"""

        # Call Groq AI
        print(f"[IMPROVE] Type: {improvement_type}, Target: {target_duration}s")
        if custom_instructions:
            print(f"[IMPROVE] Custom instructions: {custom_instructions[:100]}...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": improvement_prompts[improvement_type]}
            ],
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            stream=False
        )

        improved_text = response.choices[0].message.content.strip()

        # Calculate metrics
        original_word_count = len(current_text.split())
        improved_word_count = len(improved_text.split())
        estimated_duration = round(improved_word_count / 2.5, 1)

        # Generate changes summary
        word_diff = improved_word_count - original_word_count
        if improvement_type == 'custom':
            changes_summary = f"Custom improvement applied"
        elif improvement_type == 'enhance':
            changes_summary = f"Enhanced emotional impact and engagement"
        elif improvement_type == 'expand':
            changes_summary = f"Expanded with details (+{word_diff} words)"
        elif improvement_type == 'refine':
            changes_summary = f"Refined pacing and grammar"
        elif improvement_type == 'make_viral':
            changes_summary = f"Optimized for virality with hooks and tension"

        # Update series metadata if provided
        if series_id:
            try:
                manager = StoryContextManager()
                manager.update_part_metadata(
                    series_id,
                    part_number,
                    {
                        'improved': True,
                        'improvement_type': improvement_type,
                        'original_word_count': original_word_count,
                        'improved_word_count': improved_word_count
                    }
                )
                print(f"[IMPROVE] Updated series {series_id} part {part_number} metadata")
            except Exception as e:
                print(f"[WARN] Could not update series metadata: {e}")

        return jsonify({
            'success': True,
            'original_text': current_text,
            'improved_text': improved_text,
            'improvement_type': improvement_type,
            'changes_summary': changes_summary,
            'word_count': improved_word_count,
            'estimated_duration': estimated_duration,
            'metrics': {
                'original_words': original_word_count,
                'improved_words': improved_word_count,
                'word_difference': word_diff,
                'original_duration': round(original_word_count / 2.5, 1),
                'improved_duration': estimated_duration
            }
        })

    except Exception as e:
        print(f"[ERROR] Story improvement failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate/audio', methods=['POST'])
def generate_audio():
    """Generate TTS audio with job tracking and optional subtitle generation"""
    data = request.json
    text = data.get('text')
    voice = data.get('voice', 'default')
    use_elevenlabs = data.get('use_elevenlabs', bool(ELEVENLABS_API_KEY))
    series_id = data.get('series_id')
    part_number = data.get('part_number', 1)
    generate_subs = data.get('generate_subtitles', False)
    words_per_chunk = data.get('words_per_chunk', 2)

    print(f"[AUDIO] Voice requested: {voice}")
    print(f"[AUDIO] Using ElevenLabs: {use_elevenlabs}")
    print(f"[AUDIO] Generate subtitles: {generate_subs}")
    if series_id:
        print(f"[AUDIO] Series ID: {series_id}, Part: {part_number}")

    if not text:
        return jsonify({'success': False, 'error': 'Text is required'}), 400

    # Create job
    import time
    job_id = f"audio_{int(time.time() * 1000)}"
    job = create_job(job_id, JobType.AUDIO, metadata={'voice': voice, 'use_elevenlabs': use_elevenlabs, 'series_id': series_id})

    try:
        update_job(job_id, status=JobStatus.RUNNING, progress=20)

        # Generate unique filename based on text + voice hash
        audio_hash = abs(hash(text + voice))
        output_path = PENDING_DIR / f"audio_{audio_hash}.mp3"

        update_job(job_id, progress=40)

        # Initialize variables for subtitle generation
        alignment_data = None
        timing_source = None
        subtitles = None

        if use_elevenlabs and ELEVENLABS_API_KEY:
            tts = ElevenLabsTTS(ELEVENLABS_API_KEY)

            # Use timing API if subtitles requested
            if generate_subs:
                print("[AUDIO] Using ElevenLabs timing API for perfect subtitle sync")
                audio_path, alignment_data = tts.generate_audio_with_timestamps(
                    text=text,
                    voice=voice,
                    output_path=str(output_path)
                )
                timing_source = 'elevenlabs_api'
            else:
                # Standard audio generation without timing
                audio_path = tts.generate_audio(text, voice=voice, output_path=str(output_path))
                timing_source = 'none'

            # Get duration
            temp_tts = TTSGenerator()
            duration = temp_tts.get_audio_duration(audio_path)
        else:
            # gTTS fallback
            tts = TTSGenerator()
            audio_path = tts.generate_audio(text, output_path=str(output_path))
            duration = tts.get_audio_duration(audio_path)
            timing_source = 'linear_estimation'

        update_job(job_id, progress=70)

        # Generate subtitles if requested
        if generate_subs:
            sub_gen = SubtitleGenerator(words_per_chunk=words_per_chunk)

            if alignment_data:
                # Use precise timing from ElevenLabs API
                print(f"[AUDIO] Generating subtitles from {len(alignment_data.characters)} character timestamps")

                # CRITICAL: Use the text that was actually sent to ElevenLabs (with emotional markers)
                # by reconstructing it from the character alignment data
                actual_text = ''.join(alignment_data.characters)
                print(f"[AUDIO] Text length - Original: {len(text)}, Actual (with emotion): {len(actual_text)}")

                word_timings = sub_gen.convert_char_timing_to_words(
                    text=actual_text,  # Use reconstructed text, not original
                    char_start_times=alignment_data.character_start_times_seconds,
                    char_end_times=alignment_data.character_end_times_seconds,
                    characters=alignment_data.characters
                )
                subtitles_tuples = sub_gen.generate_subtitles_from_word_timing(word_timings)
                print(f"[AUDIO] Generated {len(subtitles_tuples)} perfectly synced subtitles")
            else:
                # Fallback to linear timing
                print(f"[AUDIO] Generating subtitles using linear timing (fallback)")
                subtitles_tuples = sub_gen.generate_subtitles(text, duration)

            # Convert to dict format
            subtitles = [{'start': s, 'end': e, 'text': t} for s, e, t in subtitles_tuples]
            print(f"[AUDIO] Subtitle timing source: {timing_source}")

        update_job(job_id, progress=85)

        # Link audio to series if series_id provided
        if series_id:
            try:
                manager = StoryContextManager()
                from pathlib import Path
                filename = Path(audio_path).name
                manager.link_assets_to_part(series_id, part_number, audio_path=filename)
                print(f"[AUDIO] Linked {filename} to series {series_id} part {part_number}")
            except Exception as e:
                print(f"[AUDIO] Warning: Failed to link audio to series: {e}")

        # Mark complete
        result_data = {
            'audio_path': str(audio_path),
            'duration': duration
        }
        if subtitles is not None:
            result_data['subtitles'] = subtitles
            result_data['timing_source'] = timing_source

        update_job(job_id, status=JobStatus.COMPLETED, progress=100, result=result_data)

        response_data = {
            'success': True,
            'job_id': job_id,
            'audio_path': str(audio_path),
            'duration': duration
        }
        if subtitles is not None:
            response_data['subtitles'] = subtitles
            response_data['timing_source'] = timing_source

        return jsonify(response_data)
    except Exception as e:
        import traceback
        print(f"[AUDIO] ERROR: {str(e)}")
        print(f"[AUDIO] Traceback:\n{traceback.format_exc()}")
        update_job(job_id, status=JobStatus.FAILED, error=str(e))
        return jsonify({'success': False, 'error': str(e), 'job_id': job_id}), 500

@app.route('/api/generate/subtitles', methods=['POST'])
def generate_subtitles():
    """Generate subtitles with job tracking"""
    data = request.json
    text = data.get('text')
    duration = data.get('duration')
    words_per_chunk = data.get('words_per_chunk', 2)

    if not text or not duration:
        return jsonify({'success': False, 'error': 'Text and duration required'}), 400

    # Create job
    import time
    job_id = f"subs_{int(time.time() * 1000)}"
    job = create_job(job_id, JobType.SUBTITLES, metadata={'words_per_chunk': words_per_chunk})

    try:
        update_job(job_id, status=JobStatus.RUNNING, progress=30)

        sub_gen = SubtitleGenerator(words_per_chunk=words_per_chunk)
        subtitles = sub_gen.generate_subtitles(text, duration)

        subtitle_dicts = [{'start': s, 'end': e, 'text': t} for s, e, t in subtitles]

        # Mark complete
        update_job(job_id, status=JobStatus.COMPLETED, progress=100, result={'subtitles': subtitle_dicts})

        return jsonify({
            'success': True,
            'job_id': job_id,
            'subtitles': subtitle_dicts
        })
    except Exception as e:
        update_job(job_id, status=JobStatus.FAILED, error=str(e))
        return jsonify({'success': False, 'error': str(e), 'job_id': job_id}), 500

@app.route('/api/effects/generate', methods=['POST'])
def generate_effects():
    """Generate effect timeline from natural language prompt using AI.

    Request body:
        {
            "prompt": "Add zoom at emphasis words",
            "story_text": "Full story text...",
            "audio_duration": 65.5,
            "subtitles": [...]  // optional
        }

    Returns:
        {
            "success": true,
            "timeline": [...],  // Array of effect objects
            "preview": "Generated 3 effects"
        }
    """
    try:
        data = request.json

        prompt = data.get('prompt')
        story_text = data.get('story_text')
        audio_duration = data.get('audio_duration', 60.0)
        subtitles = data.get('subtitles')

        if not prompt or not story_text:
            return jsonify({
                'success': False,
                'error': 'prompt and story_text are required'
            }), 400

        # Initialize effect agent
        from src.agents import EffectAgent

        agent = EffectAgent(api_key=GROQ_API_KEY)

        # Generate timeline from prompt
        print(f"[EFFECT AGENT] Processing prompt: '{prompt}'")
        timeline = agent.generate_timeline_from_prompt(
            prompt=prompt,
            story_text=story_text,
            audio_duration=audio_duration,
            subtitles=subtitles
        )

        return jsonify({
            'success': True,
            'timeline': timeline,
            'preview': f"Generated {len(timeline)} effect(s)",
            'effect_count': len(timeline)
        })

    except Exception as e:
        print(f"[EFFECT AGENT ERROR] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate/video', methods=['POST'])
def generate_video():
    """Generate complete video with job tracking"""
    data = request.json

    # Extract parameters
    story_text = data.get('story_text')
    genre = data.get('genre', 'comedy')
    audio_path = data.get('audio_path')
    subtitles = data.get('subtitles')
    background_video = data.get('background_video')
    effect_timeline = data.get('effect_timeline')  # Optional effects from JSON
    series_id = data.get('series_id')
    part_number = data.get('part_number', 1)

    if not story_text or not audio_path:
        return jsonify({'success': False, 'error': 'Story text and audio required'}), 400

    # Create job
    import time
    job_id = f"video_{int(time.time() * 1000)}"
    job = create_job(job_id, JobType.VIDEO, metadata={'genre': genre, 'background': background_video, 'series_id': series_id})

    # Legacy progress dict (keep for backwards compat)
    video_id = job_id
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

        # Progress callback that updates both legacy and job tracker
        def update_progress(progress, status):
            # Map 0-100% rendering progress to 20-90% overall progress
            overall_progress = 20 + int(progress * 0.7)
            video_progress[video_id] = {'progress': overall_progress, 'status': status}
            update_job(job_id, status=JobStatus.RUNNING, progress=overall_progress)

        video_path = composer.create_video(
            audio_path=audio_path,
            subtitles=subtitle_tuples,
            output_path=str(output_path),
            story_metadata={'story': story_text, 'genre': genre},
            genre=genre,
            background_video=str(bg_path) if bg_path else None,
            progress_callback=update_progress,
            effect_timeline=effect_timeline  # Pass effects to composer
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

        # Link video to series if series_id provided
        if series_id:
            try:
                manager = StoryContextManager()
                from pathlib import Path
                filename = Path(video_path).name
                manager.link_assets_to_part(series_id, part_number, video_path=filename)
                print(f"[VIDEO] Linked {filename} to series {series_id} part {part_number}")
            except Exception as e:
                print(f"[VIDEO] Warning: Failed to link video to series: {e}")

        # Mark job complete
        update_job(job_id, status=JobStatus.COMPLETED, progress=100, result={'video_path': str(video_path), 'metadata': metadata})

        # Clean up progress after a delay
        import threading
        def cleanup():
            import time
            time.sleep(10)
            video_progress.pop(video_id, None)
        threading.Thread(target=cleanup, daemon=True).start()

        return jsonify({
            'success': True,
            'job_id': job_id,
            'video_id': video_id,
            'video_path': str(video_path),
            'metadata': metadata
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[VIDEO] ERROR: {str(e)}")
        print(f"[VIDEO] Traceback:\n{error_trace}")
        update_job(job_id, status=JobStatus.FAILED, error=str(e))
        return jsonify({'success': False, 'error': str(e), 'job_id': job_id}), 500

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

@app.route('/api/files/audios', methods=['GET'])
def get_audios():
    """List generated audio files"""
    audios = []
    for f in PENDING_DIR.glob("audio_*.mp3"):
        stat = f.stat()

        # Try to get duration
        try:
            from src.generation.tts_generator import TTSGenerator
            tts = TTSGenerator()
            duration = tts.get_audio_duration(str(f))
        except:
            duration = 0

        audios.append({
            'name': f.name,
            'path': str(f),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'duration': duration
        })

    audios.sort(key=lambda x: x['modified'], reverse=True)

    return jsonify({'success': True, 'audios': audios})

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
    response = send_from_directory(PENDING_DIR, filename, mimetype='audio/mpeg')
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/files/background/<filename>', methods=['GET'])
def serve_background(filename):
    """Serve background video file"""
    return send_from_directory(BACKGROUNDS_DIR, filename, mimetype='video/mp4')

# ==================== MULTI-PART STORY SERIES ====================

@app.route('/api/stories/series', methods=['POST'])
def create_story_series():
    """Create a new multi-part story series"""
    try:
        data = request.json
        genre = data.get('genre')
        total_parts = data.get('total_parts')
        theme = data.get('theme')
        base_prompt = data.get('base_prompt')

        if not genre or not total_parts or not theme:
            return jsonify({
                'success': False,
                'error': 'genre, total_parts, and theme are required'
            }), 400

        valid_genres = list_genres()
        if genre not in valid_genres:
            return jsonify({
                'success': False,
                'error': f'Invalid genre. Must be one of: {", ".join(valid_genres)}'
            }), 400

        if not isinstance(total_parts, int) or total_parts < 1 or total_parts > 10:
            return jsonify({
                'success': False,
                'error': 'total_parts must be between 1 and 10'
            }), 400

        manager = StoryContextManager()
        result = manager.create_series(
            genre=genre,
            total_parts=total_parts,
            theme=theme,
            base_prompt=base_prompt
        )

        return jsonify({
            'success': True,
            'story_id': result['story_id'],
            'series_metadata': result['series_metadata']
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stories/series/<story_id>/next-part', methods=['POST'])
def generate_next_series_part(story_id):
    """Generate next part in a story series"""
    try:
        data = request.json or {}
        target_duration = data.get('target_duration', 75)

        manager = StoryContextManager()
        result = manager.generate_next_part(
            story_id=story_id,
            target_duration=target_duration
        )

        return jsonify({
            'success': True,
            'story_text': result['story_text'],
            'part_metadata': result['part_metadata'],
            'part_number': result['part_metadata']['part'],
            'duration': result['duration']
        }), 201

    except ValueError as e:
        error_msg = str(e)
        # Series complete should return 400, series not found should return 404
        if "complete" in error_msg.lower():
            return jsonify({'success': False, 'error': error_msg}), 400
        else:
            return jsonify({'success': False, 'error': error_msg}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stories/series/<story_id>', methods=['GET'])
def get_story_series(story_id):
    """Get information about a specific story series"""
    try:
        manager = StoryContextManager()
        series = manager.get_series(story_id)

        if not series:
            return jsonify({
                'success': False,
                'error': 'Story series not found'
            }), 404

        metadata = series.get('metadata', {})
        return jsonify({
            'success': True,
            'story_id': series['story_id'],
            'parts': series['parts'],
            'current_part': series['current_part'],
            'genre': metadata.get('genre'),
            'theme': metadata.get('theme'),
            'total_parts': metadata.get('total_parts'),
            'metadata': series['metadata']
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stories/series', methods=['GET'])
def list_story_series():
    """List all story series"""
    try:
        manager = StoryContextManager()
        series_list = manager.list_all_series()

        return jsonify({
            'success': True,
            'series': series_list
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stories/series/<story_id>', methods=['DELETE'])
def delete_story_series(story_id):
    """Delete a story series and all associated files"""
    try:
        manager = StoryContextManager()
        manager.delete_series(story_id)

        return jsonify({
            'success': True,
            'message': f'Series {story_id} deleted successfully'
        })

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        print(f"[DELETE SERIES ERROR] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== UNIFIED SERIES API ====================

@app.route('/api/series', methods=['GET'])
def get_all_series():
    """Get all series (unified endpoint - singles + multi-part)"""
    try:
        manager = StoryContextManager()
        series_list = manager.list_all_series()

        # Annotate with asset status
        for series in series_list:
            parts = series.get('parts', [])
            series['has_audio'] = any(p.get('audio_path') for p in parts)
            series['has_video'] = any(p.get('video_path') for p in parts)
            series['audio_count'] = sum(1 for p in parts if p.get('audio_path'))
            series['video_count'] = sum(1 for p in parts if p.get('video_path'))

        return jsonify({
            'success': True,
            'series': series_list
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/series/<series_id>/assets', methods=['GET'])
def get_series_assets(series_id):
    """Get all audio/video assets for a series"""
    try:
        manager = StoryContextManager()
        series = manager.get_series(series_id)

        if not series:
            return jsonify({
                'success': False,
                'error': 'Series not found'
            }), 404

        assets = {
            'stories': [{'part': p['part'], 'text': p['story_text'], 'word_count': p['word_count']} for p in series['parts']],
            'audios': [{'part': p['part'], 'path': p.get('audio_path')} for p in series['parts'] if p.get('audio_path')],
            'videos': [{'part': p['part'], 'path': p.get('video_path')} for p in series['parts'] if p.get('video_path')]
        }

        return jsonify({
            'success': True,
            'series_id': series_id,
            'assets': assets
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/series/<series_id>', methods=['PATCH'])
def update_series(series_id):
    """Update series metadata (e.g., total_parts)"""
    try:
        data = request.json
        new_total_parts = data.get('total_parts')

        if not new_total_parts:
            return jsonify({
                'success': False,
                'error': 'total_parts is required'
            }), 400

        manager = StoryContextManager()
        manager.update_series_total_parts(series_id, new_total_parts)

        return jsonify({
            'success': True,
            'message': f'Updated series {series_id} to {new_total_parts} total parts'
        })

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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

# ==================== JOB TRACKING ====================

@app.route('/api/jobs/active', methods=['GET'])
def get_active_jobs():
    """Get all active jobs (pending/running)"""
    try:
        jobs = list_active_jobs()
        return jsonify({
            'success': True,
            'jobs': [job.to_dict() for job in jobs]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jobs/recent', methods=['GET'])
def get_recent_jobs():
    """Get recent jobs (last 50)"""
    try:
        limit = request.args.get('limit', 50, type=int)
        jobs = list_user_jobs(limit=limit)
        return jsonify({
            'success': True,
            'jobs': [job.to_dict() for job in jobs]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status and result"""
    try:
        job = get_job(job_id)
        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        return jsonify({
            'success': True,
            'job': job.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jobs/<job_id>', methods=['DELETE'])
def cancel_job(job_id):
    """Cancel/delete a job"""
    try:
        success = delete_job(job_id)
        if not success:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        return jsonify({'success': True, 'message': 'Job deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'version': '2.0.0-mvp'
    })


@app.route('/api/cache/size', methods=['GET'])
def get_cache_size():
    """Get total cache size in MB"""
    from src.generation.tts_elevenlabs import ElevenLabsTTS
    cache_dir = ElevenLabsTTS.get_cache_dir()

    if not cache_dir.exists():
        return jsonify({'success': True, 'size_mb': 0})

    total_size = sum(f.stat().st_size for f in cache_dir.glob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)

    return jsonify({'success': True, 'size_mb': size_mb})


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cached audio files"""
    from src.generation.tts_elevenlabs import ElevenLabsTTS
    cache_dir = ElevenLabsTTS.get_cache_dir()

    if not cache_dir.exists():
        return jsonify({'success': True, 'files_deleted': 0})

    files_deleted = 0
    for f in cache_dir.glob('*'):
        if f.is_file():
            f.unlink()
            files_deleted += 1

    return jsonify({'success': True, 'files_deleted': files_deleted})


@app.route('/api/config/quality', methods=['POST'])
def set_quality_preset():
    """Set video quality preset"""
    data = request.json
    quality = data.get('quality', 'viral')

    presets = {
        'draft': {'bitrate': '3000k', 'preset': 'faster', 'crf': '23'},
        'standard': {'bitrate': '5000k', 'preset': 'medium', 'crf': '21'},
        'viral': {'bitrate': '8000k', 'preset': 'slow', 'crf': '18'}
    }

    if quality not in presets:
        return jsonify({'success': False, 'error': 'Invalid quality preset'}), 400

    preset = presets[quality]

    # Update .env file
    env_path = Path('.env')
    env_lines = []

    if env_path.exists():
        with open(env_path, 'r') as f:
            env_lines = f.readlines()

    # Update or add quality settings
    settings = {
        'VIDEO_BITRATE': preset['bitrate'],
        'VIDEO_PRESET': preset['preset'],
        'VIDEO_CRF': preset['crf']
    }

    updated_keys = set()
    for i, line in enumerate(env_lines):
        for key, value in settings.items():
            if line.startswith(f"{key}="):
                env_lines[i] = f"{key}={value}\n"
                updated_keys.add(key)

    # Add new keys
    for key, value in settings.items():
        if key not in updated_keys:
            env_lines.append(f"{key}={value}\n")

    # Save
    with open(env_path, 'w') as f:
        f.writelines(env_lines)

    return jsonify({'success': True, 'message': f'Quality preset "{quality}" saved', 'preset': preset})


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

# ==================== ANALYTICS ENDPOINTS ====================

@app.route('/api/analytics/detailed', methods=['GET'])
def get_detailed_analytics():
    """Get detailed analytics with real video metadata"""
    try:
        from moviepy import VideoFileClip
        import time

        videos = []
        video_files = list(PENDING_DIR.glob("*.mp4"))

        for video_path in video_files:
            try:
                stats = video_path.stat()
                try:
                    with VideoFileClip(str(video_path)) as clip:
                        duration = clip.duration
                except:
                    duration = 60

                name = video_path.stem
                genre = 'unknown'
                for g in ['comedy', 'terror', 'aita', 'genz_chaos', 'relationship_drama']:
                    if g in name.lower():
                        genre = g
                        break

                videos.append({
                    'name': video_path.name,
                    'size': stats.st_size,
                    'modified': stats.st_mtime,
                    'duration': duration,
                    'genre': genre,
                    'monetizable': duration >= 60
                })
            except Exception as e:
                continue

        total_videos = len(videos)
        total_duration = sum(v['duration'] for v in videos)
        total_size = sum(v['size'] for v in videos)
        week_ago = time.time() - (7 * 24 * 60 * 60)
        this_week = len([v for v in videos if v['modified'] > week_ago])

        genre_counts = {}
        for v in videos:
            genre = v['genre']
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

        monetizable_count = len([v for v in videos if v['monetizable']])

        # Calculate daily counts for past 7 days
        from datetime import datetime, timedelta
        today = datetime.now()
        weekly_counts = {}
        for i in range(7):
            day = today - timedelta(days=6-i)
            day_key = day.strftime('%Y-%m-%d')
            weekly_counts[day_key] = 0

        for v in videos:
            video_date = datetime.fromtimestamp(v['modified']).strftime('%Y-%m-%d')
            if video_date in weekly_counts:
                weekly_counts[video_date] += 1

        weekly_data = [
            {
                'label': datetime.strptime(day, '%Y-%m-%d').strftime('%a'),
                'count': count
            }
            for day, count in sorted(weekly_counts.items())
        ]

        return jsonify({
            'success': True,
            'stats': {
                'totalVideos': total_videos,
                'totalDuration': total_duration,
                'avgDuration': total_duration / total_videos if total_videos > 0 else 0,
                'totalSize': total_size,
                'avgSize': total_size / total_videos if total_videos > 0 else 0,
                'thisWeek': this_week,
                'monetizable': monetizable_count,
                'weeklyData': weekly_data,
                'monetizablePercentage': (monetizable_count / total_videos * 100) if total_videos > 0 else 0
            },
            'genreBreakdown': genre_counts,
            'recentVideos': sorted(videos, key=lambda x: x['modified'], reverse=True)[:10]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
