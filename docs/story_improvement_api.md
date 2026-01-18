# Story Improvement API

## Endpoint
`POST /api/stories/improve`

## Purpose
Improve existing story text using AI without completely regenerating it. This allows creators to enhance, expand, refine, or optimize stories for virality while maintaining the core narrative.

## Use Cases
1. **Enhance** - Story is good but needs more emotional impact
2. **Expand** - Story is too short for monetization (need 60+ seconds)
3. **Refine** - Story has grammar/pacing issues or weak hooks
4. **Make Viral** - Story needs optimization for TikTok/Shorts engagement

## Request Format

### Basic Request
```json
{
  "current_text": "The story text you want to improve",
  "improvement_type": "enhance",
  "genre": "comedy",
  "target_duration": 75
}
```

### With Series Tracking
```json
{
  "current_text": "The story text you want to improve",
  "improvement_type": "make_viral",
  "genre": "terror",
  "target_duration": 80,
  "series_id": "story_abc123",
  "part_number": 2
}
```

## Parameters

### Required
- `current_text` (string) - The story text to improve

### Optional
- `improvement_type` (string) - Default: "enhance"
  - `enhance` - Make more engaging/dramatic
  - `expand` - Add details to reach target duration
  - `refine` - Fix grammar, improve pacing
  - `make_viral` - Optimize for virality
- `genre` (string) - Default: "comedy"
  - Options: comedy, terror, aita, relationship_drama, genz_chaos
- `target_duration` (number) - Default: 75 seconds
  - Recommended: 60-90s for monetization
- `series_id` (string) - Optional series ID for metadata tracking
- `part_number` (number) - Default: 1, part number in series

## Response Format

```json
{
  "success": true,
  "original_text": "Original story...",
  "improved_text": "Improved story with enhancements...",
  "improvement_type": "enhance",
  "changes_summary": "Enhanced emotional impact and engagement",
  "word_count": 134,
  "estimated_duration": 53.6,
  "metrics": {
    "original_words": 46,
    "improved_words": 134,
    "word_difference": 88,
    "original_duration": 18.4,
    "improved_duration": 53.6
  }
}
```

## Examples

### Example 1: Enhance Emotional Impact
```bash
curl -X POST http://localhost:5000/api/stories/improve \
  -H "Content-Type: application/json" \
  -d '{
    "current_text": "I woke up this morning and found a weird note on my door. It said Your coffee maker is plotting against you. I thought it was a prank. But then my coffee maker started making coffee at 3 AM every night. Now I am scared to sleep.",
    "improvement_type": "enhance",
    "genre": "comedy",
    "target_duration": 75
  }'
```

**Result**: Story becomes more dramatic and engaging with better word choice and emotional emphasis.

### Example 2: Expand for Monetization
```bash
curl -X POST http://localhost:5000/api/stories/improve \
  -H "Content-Type: application/json" \
  -d '{
    "current_text": "I found a box in my attic. Inside was a diary from 1952. The last entry said tomorrow I die. The date was today.",
    "improvement_type": "expand",
    "genre": "terror",
    "target_duration": 85
  }'
```

**Result**: Story expands to 200+ words with vivid details and sensory descriptions.

### Example 3: Make Viral
```bash
curl -X POST http://localhost:5000/api/stories/improve \
  -H "Content-Type: application/json" \
  -d '{
    "current_text": "My roommate never cleans. I have asked nicely a hundred times. Yesterday I found a science experiment growing in the sink. It is time for war.",
    "improvement_type": "make_viral",
    "genre": "aita",
    "target_duration": 70
  }'
```

**Result**: Story optimized with powerful hooks, emotional tension, and viral pacing.

### Example 4: Refine Grammar and Pacing
```bash
curl -X POST http://localhost:5000/api/stories/improve \
  -H "Content-Type: application/json" \
  -d '{
    "current_text": "So like my boyfriend bought me flowers yesterday but they were the wrong color and also he forgot my favorite restaurant so we went to that place I hate and also I was really mad because he was on his phone the whole time texting his friend about the game and I was like so upset.",
    "improvement_type": "refine",
    "genre": "relationship_drama",
    "target_duration": 60
  }'
```

**Result**: Cleaned up grammar, varied sentence length, improved flow.

## Error Responses

### Missing Required Field
```json
{
  "success": false,
  "error": "current_text is required"
}
```
HTTP Status: 400

### Invalid Improvement Type
```json
{
  "success": false,
  "error": "improvement_type must be one of: enhance, expand, refine, make_viral"
}
```
HTTP Status: 400

### API Error
```json
{
  "success": false,
  "error": "Story improvement failed: [error details]"
}
```
HTTP Status: 500

## Performance
- **Average response time**: 3-5 seconds
- **Model**: Groq AI (llama-3.3-70b-versatile)
- **Temperature**: 0.7 (balanced creativity)
- **Max tokens**: 800

## Best Practices

1. **Choose the right improvement type**:
   - Use `enhance` when story length is good but needs more impact
   - Use `expand` when story is under 60 seconds
   - Use `refine` for grammar/pacing fixes
   - Use `make_viral` for TikTok optimization

2. **Set appropriate target duration**:
   - 60-90 seconds optimal for monetization
   - 75 seconds is the sweet spot

3. **Track improvements in series**:
   - Always provide `series_id` and `part_number` when working with multi-part stories
   - Metadata is automatically updated for tracking

4. **Iterate carefully**:
   - Don't over-improve (can lose authenticity)
   - Test the improved version with TTS before finalizing

## Integration with Workflow

```
1. Generate story → POST /api/generate/story
2. Review story → Too short? Wrong tone?
3. Improve story → POST /api/stories/improve
4. Generate audio → POST /api/generate/audio
5. Generate video → POST /api/generate/video
```

## Technical Details

### AI System Prompt
The endpoint uses genre-specific system prompts that maintain:
- TikTok/YouTube Shorts viral style
- Fast-paced, engaging narrative
- Natural, human-like language (avoid AI detection)
- Varied sentence length
- Emotional emphasis

### Improvement Prompts
Each improvement type uses carefully crafted prompts that:
- Preserve the original storyline
- Target specific duration requirements
- Apply genre-appropriate optimizations
- Return only the story text (no meta-commentary)

### Series Metadata
When `series_id` is provided, the endpoint updates part metadata with:
- `improved`: true
- `improvement_type`: The type used
- `original_word_count`: Original word count
- `improved_word_count`: New word count

## Limitations

1. **Not a replacement for generation**: This improves existing text, doesn't create new stories
2. **Context preservation**: Major plot changes require regeneration
3. **Language**: Currently optimized for English only
4. **Rate limits**: Subject to Groq API rate limits (typically 30 req/min)

## Future Enhancements

- [ ] Batch improvement (multiple stories at once)
- [ ] A/B testing (generate multiple improved versions)
- [ ] Custom improvement instructions
- [ ] Multi-language support
- [ ] Improvement history/undo functionality
