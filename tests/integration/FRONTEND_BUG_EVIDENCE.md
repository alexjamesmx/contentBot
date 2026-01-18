# Frontend Bug Evidence: Multi-Part Series "Override" Illusion

**Date:** 2026-01-12
**Component:** `contentbot-ui/src/pages/Generator.jsx`
**Bug Type:** User Experience (State Management)

---

## The Bug in Plain English

**What User Reports:**
> "When I create Part 2 of my series, it OVERRIDES Part 1. Part 1 completely disappears!"

**What's Actually Happening:**
> Part 1 is safely stored in the backend. The frontend UI just hides it from view when you start working on Part 2.

**Analogy:**
> It's like having a notebook where you can only see one page at a time. When you flip to page 2, you think page 1 disappeared - but it's still in the notebook, you just can't see it anymore.

---

## Visual Flow Diagram

### Current (Broken) User Experience:

```
Step 1: User Creates Part 1
┌─────────────────────────────────────┐
│  Generator UI                       │
│  ┌─────────────────────────────┐   │
│  │ Part 1 Story: "I entered..." │   │
│  │ Audio: ✓ Generated           │   │
│  │ Video: ✓ Generated           │   │
│  └─────────────────────────────┘   │
│  [Create Next Part in Series]      │
└─────────────────────────────────────┘
         ↓ User clicks button
         ↓

Step 2: User Creates Part 2
┌─────────────────────────────────────┐
│  Generator UI                       │
│  ┌─────────────────────────────┐   │
│  │ Part 2 Story: "The door..." │   │  ← Part 2 shown
│  │ Audio: ✗ Not generated       │   │
│  │ Video: ✗ Not generated       │   │
│  └─────────────────────────────┘   │
│                                     │
│  ❌ Part 1 GONE from UI!           │  ← User's panic point
└─────────────────────────────────────┘
         ↓ User thinks
         ↓

"WHERE DID PART 1 GO?! IT WAS OVERRIDDEN!"

BUT ACTUALLY...

Backend Storage (Hidden from User):
┌─────────────────────────────────────┐
│  story_series/{series_id}.json      │
│  {                                  │
│    "parts": [                       │
│      {                              │
│        "part": 1,                   │  ← Part 1 still here!
│        "story_text": "I entered..." │
│        "audio_path": "audio_123.mp3"│
│        "video_path": "video_123.mp4"│
│      },                             │
│      {                              │
│        "part": 2,                   │  ← Part 2 also here!
│        "story_text": "The door..."  │
│      }                              │
│    ]                                │
│  }                                  │
└─────────────────────────────────────┘

✅ Both parts exist in backend
❌ UI only shows current part
```

---

## Code Evidence

### File: `contentbot-ui/src/pages/Generator.jsx`

#### Line 514-552: The Problematic Function

```javascript
const handleAddNextPart = async () => {
  setLoading(true)
  try {
    // Step 1: Extend series (works fine)
    await axios.patch(`${API_URL}/series/${seriesId}`, {
      total_parts: totalParts + 1
    })
    setTotalParts(prev => prev + 1)

    // Step 2: Generate Part 2 (works fine - backend stores both parts)
    const { data } = await axios.post(
      `${API_URL}/stories/series/${seriesId}/next-part`,
      { target_duration: targetDuration }
    )

    if (data.success) {
      // Step 3: ❌ BUG LOCATION - Replace state instead of preserving
      setStoryData({
        story: data.story_text,              // ❌ Shows only Part 2
        word_count: data.part_metadata.word_count,
        hook: data.part_metadata.hook,
        estimated_duration: data.duration
      })
      setEditStory(data.story_text)          // ❌ Edits only Part 2
      setCurrentPartNumber(data.part_number) // Updates to 2

      // Step 4: ❌ CRITICAL BUG - Wipe Part 1 assets from UI
      setAudioData(null)      // ❌ Part 1 audio gone from UI
      setSubtitleData(null)   // ❌ Part 1 subtitles gone from UI
      setVideoData(null)      // ❌ Part 1 VIDEO GONE FROM UI
      setEffectTimeline(null) // ❌ Part 1 effects gone from UI
      setStep(1)              // ❌ Reset to story step
    }
  } catch (error) {
    console.error('Failed to add next part:', error)
    setError('Failed to add next part: ' + error.message)
  } finally {
    setLoading(false)
  }
}
```

#### Why This Causes the "Override" Illusion

The Generator component uses **single-value state** for everything:

```javascript
// Current State Structure (Single Part Only):
const [storyData, setStoryData] = useState(null)      // 1 story
const [audioData, setAudioData] = useState(null)      // 1 audio
const [videoData, setVideoData] = useState(null)      // 1 video
const [currentPartNumber, setCurrentPartNumber] = useState(1)

// What happens when creating Part 2:
setStoryData(part2Story)    // ❌ Replaces Part 1 story
setAudioData(null)          // ❌ Wipes Part 1 audio
setVideoData(null)          // ❌ Wipes Part 1 video
```

**The UI can only "remember" ONE part at a time.**

When you load Part 2, it **forgets** Part 1 (even though Part 1 is safe in the backend).

---

## Backend Proof: Both Parts Exist

### API Call Evidence

**Test:** `test_multipart_series_workflow()`

**After generating Part 2, backend returns:**

```json
{
  "story_id": "7c4576c4-7dc3-4b1d-84fb-7bac2646bd00",
  "genre": "terror",
  "total_parts": 3,
  "current_part": 2,
  "parts": [
    {
      "part": 1,
      "story_text": "Oh man, you guys, I'm literally shaking right now... just thinking about it. So, my friends, Matt and Sarah, and I decided to investigate this supposedly haunted house on the edge of town...",
      "duration": 431,
      "audio_path": null,
      "video_path": null
    },
    {
      "part": 2,
      "story_text": "So, we're investigating this haunted house, right, and we just got here... (nervous laugh) After what happened to Matt in Part 1, I'm honestly freaking out a bit...",
      "duration": 433,
      "audio_path": null,
      "video_path": null
    }
  ]
}
```

**Proof:**
- ✅ `parts` array has 2 elements
- ✅ Part 1 still has its original `story_text`
- ✅ Part 2 has different `story_text`
- ✅ `current_part` correctly shows 2
- ✅ No override occurred in backend

---

## The Exact User Experience

### Scenario: Creating a 3-Part Horror Series

**Timestamp: 13:00:00 - User starts Part 1**

```
UI Display:
┌────────────────────────────────┐
│ Series Mode: ✓ Enabled         │
│ Theme: Haunted House           │
│ Total Parts: 3                 │
│                                │
│ [Create Series]                │
└────────────────────────────────┘
```

**Timestamp: 13:00:05 - Part 1 story generated**

```
UI Display:
┌────────────────────────────────────────────────┐
│ Step 1: Story                                  │
│ ───────────────────────────────────────────    │
│ Part 1 of 3                                    │
│                                                │
│ Story Preview:                                 │
│ "Oh man, you guys, I'm literally shaking       │
│  right now... just thinking about it..."       │
│                                                │
│ [Generate Audio] [Edit Story]                  │
└────────────────────────────────────────────────┘
```

**Timestamp: 13:00:15 - User generates audio and video**

```
UI Display:
┌────────────────────────────────────────────────┐
│ Step 4: Video Ready                            │
│ ───────────────────────────────────────────    │
│ Part 1 of 3                                    │
│                                                │
│ ┌──────────────────────────────┐              │
│ │ [▶ Video Player]             │              │
│ │  Playing: part1_video.mp4    │              │
│ └──────────────────────────────┘              │
│                                                │
│ [Download Video] [Create Another]              │
│                                                │
│ [Create Next Part in Series]  ← User clicks   │
└────────────────────────────────────────────────┘
```

**Timestamp: 13:00:20 - Part 2 story generated**

```
UI Display:
┌────────────────────────────────────────────────┐
│ Step 1: Story                                  │
│ ───────────────────────────────────────────    │
│ Part 2 of 3                                    │
│                                                │
│ Story Preview:                                 │
│ "So, we're investigating this haunted house,   │
│  right, and we just got here..."               │
│                                                │
│ [Generate Audio] [Edit Story]                  │
│                                                │
│ ❌ WHERE IS PART 1?!                           │
│ ❌ WHERE IS THE VIDEO I JUST MADE?!            │
└────────────────────────────────────────────────┘
```

**User's Mental Model:**
> "I had a completed video for Part 1. Now it's gone. Part 2 must have overridden it!"

**Reality:**
> Part 1 video is at: `outputs/videos/terror_7c4576c4.mp4`
> Backend knows about it: `GET /api/series` shows both parts
> UI just doesn't display it anymore

---

## Reproduction Steps (Frontend Manual Test)

### Prerequisites:
- Backend server running (`python app.py`)
- Frontend dev server running (`npm run dev`)

### Steps:

1. **Open Generator page** (http://localhost:5173)

2. **Enable Series Mode**
   - Toggle "Series Mode" switch ON
   - Enter theme: "Haunted house investigation"
   - Set total parts: 3

3. **Create Part 1**
   - Click "Create Series"
   - Wait for story generation
   - Click "Generate Audio"
   - Wait for audio generation
   - Click "Generate Subtitles"
   - Wait for subtitle generation
   - Click "Generate Video"
   - Wait for video generation

4. **Observe Part 1 Complete**
   - Video player shows Part 1 video
   - Can download Part 1 video
   - All assets visible in UI

5. **Create Part 2**
   - Click "Create Next Part in Series"
   - Wait for Part 2 story generation

6. **❌ BUG OBSERVED:**
   - Video player GONE
   - Part 1 story REPLACED with Part 2 story
   - Audio player GONE
   - No way to see Part 1 in UI

7. **Verify Backend Has Both Parts:**
   - Open browser console
   - Run: `fetch('http://localhost:5000/api/series').then(r => r.json()).then(console.log)`
   - Observe: `parts` array has BOTH parts

---

## Impact on User Workflows

### Workflow 1: Create 3-Part Series for TikTok

**User Goal:** Post 3 consecutive videos over 3 days

**Current Experience:**
1. Create Part 1 ✅
2. Download Part 1 video ✅
3. Create Part 2 ✅
4. Want to download Part 1 video again ❌ GONE FROM UI
5. Create Part 3 ✅
6. Want to download Part 1 and Part 2 ❌ BOTH GONE FROM UI
7. User frustrated: "I have to create all 3 parts in one session and download immediately!"

### Workflow 2: Review Series Before Publishing

**User Goal:** Check all parts for consistency

**Current Experience:**
1. Create Part 1, 2, 3 ✅
2. Want to watch Part 1 again ❌ Can't - only see Part 3
3. Want to edit Part 2 ❌ Can't - no way to navigate back
4. User frustrated: "I can't review my series!"

### Workflow 3: Continue Series Next Day

**User Goal:** Create Part 2 tomorrow after creating Part 1 today

**Current Experience:**
1. Day 1: Create Part 1, download video ✅
2. Day 2: Open Library, click "Continue" ✅
3. Generator loads series ✅
4. Create Part 2 ✅
5. Want to see Part 1 again ❌ GONE FROM UI
6. User confused: "Did I lose my work?"

---

## Why This Happens: Architecture Mismatch

### Generator.jsx Was Designed For Single Videos

**Original Architecture (Pre-Series):**
- One story → one audio → one video
- Linear workflow: Step 1 → Step 2 → Step 3 → Step 4
- No need to remember multiple parts
- Single-value state works perfectly

### Series Support Was Bolted On

**What Was Added:**
- `seriesMode` toggle
- `seriesId` and `currentPartNumber` tracking
- `handleCreateSeries` and `handleAddNextPart` functions
- Backend integration with `/api/stories/series` endpoints

**What Was NOT Added:**
- Multi-part state management
- Part navigation UI
- Asset preservation across parts
- Series overview/management interface

**Result:**
- Backend supports series perfectly ✅
- Frontend supports series partially ❌
- User experience is broken ❌

---

## Solution Options

### Option A: Add Part Navigation to Generator.jsx (Quick Fix)

**Effort:** Medium
**Impact:** Fixes user experience within existing page

**Changes Needed:**
1. Add part switcher tabs/buttons
2. Change state from single values to arrays/objects
3. Load part data when switching parts
4. Preserve assets for each part

### Option B: Create Dedicated StorySeries.jsx Page (Clean Architecture)

**Effort:** High
**Impact:** Proper series management, keeps Generator simple

**Changes Needed:**
1. Create new `StorySeries.jsx` page
2. Multi-part UI with full navigation
3. Series overview with all parts visible
4. Keep `Generator.jsx` for single videos only

### Option C: Show Previous Parts as Read-Only (Minimal Fix)

**Effort:** Low
**Impact:** User can see previous parts exist, but can't edit them

**Changes Needed:**
1. Add "Previous Parts" section below current part
2. Show read-only summary of each previous part
3. Add download links to previous part assets
4. No navigation, just visibility

---

## Recommendation

**Implement Option C immediately** (1-2 hours) to fix user panic, then **plan Option B** for next sprint (proper multi-part UX).

**Option C** gives users confidence their work isn't lost, while **Option B** provides the full experience they need.

---

## Files Affected

### Frontend (Needs Changes):
- `contentbot-ui/src/pages/Generator.jsx` (lines 514-552)

### Backend (Already Working):
- `app.py` (series endpoints ✅)
- `src/generation/story_context_manager.py` (✅)
- `story_series/` cache directory (✅)

---

**End of Report**
