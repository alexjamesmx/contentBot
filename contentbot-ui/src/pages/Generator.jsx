import { useState, useEffect, useMemo } from 'react'
import { Play, Download, Loader, CheckCircle, AlertCircle, Edit2, Check, X, ArrowLeft, Trash2, RefreshCw, Plus, Sparkles, Undo2 } from 'lucide-react'
import axios from 'axios'
import { useLocation } from 'react-router-dom'
import AudioPlayer from '../components/AudioPlayer'
import VideoPlayer from '../components/VideoPlayer'
import RecoveryNotification from '../components/RecoveryNotification'
import EffectInspector from '../components/EffectInspector'
import StoryModeSelector from '../components/StoryModeSelector'
import ManualStoryInput from '../components/ManualStoryInput'
import ImproveModal from '../components/ImproveModal'
import { useGeneratorPersistence, checkActiveJobs, pollActiveJobs } from '../hooks/useGeneratorPersistence'

const API_URL = 'http://localhost:5000/api'

const VOICES = [
  { id: 'mark', name: 'Liam (Mark)', desc: 'Energetic, TikTok creator' },
  { id: 'snap', name: 'Snap', desc: 'Playful, viral content' },
  { id: 'peter', name: 'Callum (Peter)', desc: 'Husky storyteller' },
  { id: 'viraj', name: 'Viraj', desc: 'Warm, passionate narrator' },
  { id: 'rachel', name: 'Sarah (Rachel)', desc: 'Confident, professional' },
  { id: 'adam', name: 'Adam', desc: 'Deep, authoritative' },
  { id: 'brian', name: 'Brian', desc: 'Deep, comforting' },
  { id: 'george', name: 'George', desc: 'British storyteller' },
]

const GENRE_LABELS = {
  'comedy': 'Gen-Z Comedy',
  'terror': 'Creepy Horror',
  'aita': 'AITA Drama',
  'genz_chaos': 'Unhinged Chaos',
  'relationship_drama': 'Relationship Tea'
}

export default function Generator({ reusedContent, onClearReused }) {
  const location = useLocation()
  const [genres, setGenres] = useState(['comedy', 'terror', 'aita', 'genz_chaos', 'relationship_drama'])
  const [backgrounds, setBackgrounds] = useState([])

  const [selectedGenre, setSelectedGenre] = useState('comedy')
  const [selectedBackground, setSelectedBackground] = useState('')
  const [selectedVoice, setSelectedVoice] = useState('mark')
  const [wordsPerChunk, setWordsPerChunk] = useState(4)
  const [targetDuration, setTargetDuration] = useState(75)
  const [useElevenLabs, setUseElevenLabs] = useState(true)

  const [seriesMode, setSeriesMode] = useState(false)
  const [totalParts, setTotalParts] = useState(3)
  const [seriesTheme, setSeriesTheme] = useState('')
  const [seriesId, setSeriesId] = useState(null)
  const [currentPartNumber, setCurrentPartNumber] = useState(1)
  const [seriesData, setSeriesData] = useState(null)
  const [currentPart, setCurrentPart] = useState(null)

  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [operationInProgress, setOperationInProgress] = useState(null)

  const [storyData, setStoryData] = useState(null)
  const [audioData, setAudioData] = useState(null)
  const [subtitleData, setSubtitleData] = useState(null)
  const [videoData, setVideoData] = useState(null)
  const [timingSource, setTimingSource] = useState(null)

  const [editStory, setEditStory] = useState('')
  const [editSubtitles, setEditSubtitles] = useState([])
  const [effectPrompt, setEffectPrompt] = useState('')
  const [effectTimeline, setEffectTimeline] = useState([])

  const [storyMode, setStoryMode] = useState('generate')
  const [improvePrompt, setImprovePrompt] = useState('')
  const [showImproveModal, setShowImproveModal] = useState(false)
  const [storyHistory, setStoryHistory] = useState([])

  // Recovery notification state
  const [showRecovery, setShowRecovery] = useState(false)
  const [recoveredState, setRecoveredState] = useState(null)

  // Job tracking state
  const [activeJobIds, setActiveJobIds] = useState({
    story: null,
    audio: null,
    subtitles: null,
    video: null
  })

  // Composite state for persistence
  const persistentState = useMemo(() => ({
    step, storyData, audioData, subtitleData, videoData,
    editStory, editSubtitles, effectPrompt, effectTimeline,
    selectedGenre, selectedBackground, selectedVoice,
    wordsPerChunk, targetDuration, useElevenLabs,
    seriesId, currentPartNumber, seriesMode, seriesTheme, totalParts
  }), [step, storyData, audioData, subtitleData, videoData, editStory, editSubtitles, effectPrompt, effectTimeline,
      selectedGenre, selectedBackground, selectedVoice, wordsPerChunk, targetDuration, useElevenLabs,
      seriesId, currentPartNumber, seriesMode, seriesTheme, totalParts])

  // State setter for bulk updates from persistence
  const setPersistedState = (saved) => {
    if (saved.step !== undefined) setStep(saved.step)
    if (saved.storyData) setStoryData(saved.storyData)
    if (saved.audioData) setAudioData(saved.audioData)
    if (saved.subtitleData) setSubtitleData(saved.subtitleData)
    if (saved.videoData) setVideoData(saved.videoData)
    if (saved.editStory) setEditStory(saved.editStory)
    if (saved.editSubtitles) setEditSubtitles(saved.editSubtitles)
    if (saved.effectPrompt) setEffectPrompt(saved.effectPrompt)
    if (saved.effectTimeline) setEffectTimeline(saved.effectTimeline)
    if (saved.selectedGenre) setSelectedGenre(saved.selectedGenre)
    if (saved.selectedBackground) setSelectedBackground(saved.selectedBackground)
    if (saved.selectedVoice) setSelectedVoice(saved.selectedVoice)
    if (saved.wordsPerChunk) setWordsPerChunk(saved.wordsPerChunk)
    if (saved.targetDuration) setTargetDuration(saved.targetDuration)
    if (saved.useElevenLabs !== undefined) setUseElevenLabs(saved.useElevenLabs)
    if (saved.seriesId) setSeriesId(saved.seriesId)
    if (saved.currentPartNumber) setCurrentPartNumber(saved.currentPartNumber)
    if (saved.seriesMode !== undefined) setSeriesMode(saved.seriesMode)
    if (saved.seriesTheme) setSeriesTheme(saved.seriesTheme)
    if (saved.totalParts) setTotalParts(saved.totalParts)
  }

  // Enable persistence
  const { clearSavedState, hasSavedState } = useGeneratorPersistence(persistentState, setPersistedState)

  useEffect(() => {
    loadConfig()
    initializeRecovery()
  }, [])

  // Load series and continue if coming from Library
  useEffect(() => {
    if (location.state?.continueMode && location.state?.seriesId) {
      // If seriesData is already passed, use it directly
      if (location.state?.seriesData) {
        setSeriesId(location.state.seriesId)
        setSeriesData(location.state.seriesData)
        setSelectedGenre(location.state.seriesData.genre)

        // Load the current part (the one that was clicked in Library)
        const currentPart = location.state.seriesData.parts?.find(
          p => p.part === location.state.seriesData.current_part
        )

        if (currentPart) {
          loadPartIntoGenerator(currentPart)
        } else {
          setStep(0)
        }
      } else {
        // Fallback: fetch from API if not passed
        loadSeriesAndContinue(location.state.seriesId)
      }
    }
  }, [location.state])

  // Load series data when seriesId or currentPartNumber changes
  useEffect(() => {
    if (seriesId) {
      loadSeriesData(seriesId)
    }
  }, [seriesId, currentPartNumber])

  // Poll for active jobs every 3 seconds (only when loading)
  useEffect(() => {
    if (!loading) return

    const pollInterval = setInterval(async () => {
      await pollActiveJobs(API_URL, handleJobUpdate)
    }, 3000)

    return () => clearInterval(pollInterval)
  }, [loading])

  // Handle reused content from Library
  useEffect(() => {
    if (!reusedContent) return

    if (reusedContent.type === 'story') {
      const story = reusedContent.data
      setStoryData(story)
      setEditStory(story.story)
      setSelectedGenre(story.genre || 'comedy')
      setStep(1)
      onClearReused && onClearReused()
    } else if (reusedContent.type === 'audio') {
      const audio = reusedContent.data
      setAudioData({
        audio_path: audio.path,
        duration: audio.duration
      })
      setStep(2)
      onClearReused && onClearReused()
    }
  }, [reusedContent])

  const loadConfig = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/config`)
      if (data.success) {
        setGenres(data.config.genres || [])
        setBackgrounds(data.config.assets.backgrounds || [])
      }
    } catch (error) {
      console.error('Failed to load config:', error)
    }
  }

  const initializeRecovery = async () => {
    // Check for saved state
    if (hasSavedState()) {
      const saved = localStorage.getItem('contentbot_generator_state')
      if (saved) {
        const state = JSON.parse(saved)
        // Only show recovery if there's meaningful progress (step > 0)
        if (state.step > 0) {
          setRecoveredState(state)
          setShowRecovery(true)
        }
      }
    }

    // Check for active jobs
    try {
      const jobs = await checkActiveJobs(API_URL)
      if (jobs.length > 0) {
        console.log('Found active jobs:', jobs)
        // Track active jobs for polling
        jobs.forEach(job => {
          if (job.job_type === 'video') {
            setActiveJobIds(prev => ({ ...prev, video: job.job_id }))
          }
        })
      }
    } catch (error) {
      console.error('Failed to check active jobs:', error)
    }
  }

  const handleRecoveryResume = () => {
    setShowRecovery(false)
    setRecoveredState(null)
    // State already restored by persistence hook
  }

  const handleRecoveryDismiss = () => {
    setShowRecovery(false)
    setRecoveredState(null)
    clearSavedState()
    handleReset()
  }

  const handleJobUpdate = (job) => {
    console.log('Job update:', job)

    // Update progress based on job type
    if (job.status === 'completed' && job.result) {
      switch (job.job_type) {
        case 'story':
          if (!storyData && job.result.story) {
            setStoryData(job.result)
            setEditStory(job.result.story)
          }
          break
        case 'audio':
          if (!audioData && job.result.audio_path) {
            setAudioData(job.result)
          }
          break
        case 'subtitles':
          if (!subtitleData && job.result.subtitles) {
            setSubtitleData(job.result.subtitles)
            setEditSubtitles(job.result.subtitles)
          }
          break
        case 'video':
          if (!videoData && job.result.video_path) {
            setVideoData(job.result)
            setStep(5)
            setLoading(false)
          }
          break
      }
    }

    // Handle failures
    if (job.status === 'failed') {
      setError(`Job failed: ${job.error}`)
      setLoading(false)
    }
  }

  const handleCreateSeries = async () => {
    if (operationInProgress) {
      setError('Another operation is already in progress. Please wait.')
      return
    }

    setOperationInProgress('series')
    setLoading(true)
    setError('')
    setStep(1)

    try {
      // Step 1: Create the series structure
      const { data: seriesResponse } = await axios.post(`${API_URL}/stories/series`, {
        genre: selectedGenre,
        total_parts: totalParts,
        theme: seriesTheme,
        base_prompt: `Create the first part of a story about "${seriesTheme}"`
      })

      if (seriesResponse.success) {
        const newSeriesId = seriesResponse.story_id
        setSeriesId(newSeriesId)
        setCurrentPartNumber(1)

        // Load series data
        await loadSeriesData(newSeriesId)

        // Step 2: Generate Part 1 story
        const { data: partData } = await axios.post(
          `${API_URL}/stories/series/${newSeriesId}/next-part`,
          { target_duration: targetDuration }
        )

        if (partData.success) {
          setStoryData({
            story: partData.story_text,
            word_count: partData.part_metadata.word_count,
            hook: partData.part_metadata.hook,
            estimated_duration: partData.duration
          })
          setEditStory(partData.story_text)
          setStep(1)
        }
      }
    } catch (error) {
      setError('Failed to create series: ' + (error.response?.data?.error || error.message))
      setStep(0)
    } finally {
      setLoading(false)
      setOperationInProgress(null)
    }
  }

  const handleGenerateStory = async () => {
    if (operationInProgress) {
      setError('Another operation is already in progress. Please wait.')
      return
    }

    setOperationInProgress('story')
    setLoading(true)
    setError('')
    setStep(1)

    try {
      const { data } = await axios.post(`${API_URL}/generate/story`, {
        genre: selectedGenre,
        target_duration: targetDuration
      })

      if (data.success) {
        setSeriesId(data.series_id)
        setCurrentPartNumber(data.part_number || 1)
        // ✅ Add title from top-level response
        setStoryData({
          ...data.story,
          title: data.title || 'Untitled'
        })
        setEditStory(data.story.story)
        setStep(1)
        if (data.job_id) {
          setActiveJobIds(prev => ({ ...prev, story: data.job_id }))
        }
      }
    } catch (error) {
      setError('Failed to generate story: ' + (error.response?.data?.error || error.message))
    } finally {
      setLoading(false)
      setOperationInProgress(null)
    }
  }

  const handleGenerateAudio = async () => {
    if (operationInProgress) {
      setError('Another operation is already in progress. Please wait.')
      return
    }

    setOperationInProgress('audio')
    setLoading(true)
    setError('')

    try {
      const { data } = await axios.post(`${API_URL}/generate/audio`, {
        text: editStory,
        voice: selectedVoice,
        use_elevenlabs: useElevenLabs,
        generate_subtitles: true,
        words_per_chunk: wordsPerChunk,
        series_id: seriesId,
        part_number: currentPartNumber
      })

      if (data.success) {
        setAudioData(data)

        // Extract subtitles from audio response (now included)
        if (data.subtitles && data.subtitles.length > 0) {
          setSubtitleData(data.subtitles)
          setEditSubtitles(data.subtitles)
          setTimingSource(data.timing_source || 'elevenlabs_api')
          // Show audio first, then subtitles will be available
          setStep(2)
        } else {
          // Fallback if subtitles not in response
          setStep(2)
        }

        if (data.job_id) {
          setActiveJobIds(prev => ({ ...prev, audio: data.job_id }))
        }
      }
    } catch (error) {
      setError('Failed to generate audio: ' + (error.response?.data?.error || error.message))
    } finally {
      setLoading(false)
      setOperationInProgress(null)
    }
  }

  const handleGenerateSubtitles = async () => {
    if (operationInProgress) {
      setError('Another operation is already in progress. Please wait.')
      return
    }

    setOperationInProgress('subtitles')
    setLoading(true)
    setError('')

    try {
      const { data } = await axios.post(`${API_URL}/generate/subtitles`, {
        text: editStory,
        duration: audioData.duration,
        words_per_chunk: wordsPerChunk
      })

      if (data.success) {
        setSubtitleData(data.subtitles)
        setEditSubtitles(data.subtitles)
        setStep(3)
        if (data.job_id) {
          setActiveJobIds(prev => ({ ...prev, subtitles: data.job_id }))
        }
      }
    } catch (error) {
      setError('Failed to generate subtitles: ' + (error.response?.data?.error || error.message))
    } finally {
      setLoading(false)
      setOperationInProgress(null)
    }
  }

  const handleCreateVideo = async () => {
    if (operationInProgress) {
      setError('Another operation is already in progress. Please wait.')
      return
    }

    setOperationInProgress('video')
    setLoading(true)
    setError('')
    setStep(4)

    try {
      const audioFilename = audioData.audio_path.split(/[\\/]/).pop()

      const { data } = await axios.post(`${API_URL}/generate/video`, {
        story_text: editStory,
        genre: selectedGenre,
        audio_path: audioFilename,
        subtitles: editSubtitles,
        background_video: selectedBackground || null,
        effect_timeline: effectTimeline.length > 0 ? effectTimeline : null,
        series_id: seriesId,
        part_number: currentPartNumber
      })

      if (data.success) {
        setVideoData(data)
        setStep(5)
        if (data.job_id) {
          setActiveJobIds(prev => ({ ...prev, video: data.job_id }))
        }
      }
    } catch (error) {
      setError('Failed to create video: ' + (error.response?.data?.error || error.message))
    } finally {
      setLoading(false)
      setOperationInProgress(null)
    }
  }

  const loadSeriesData = async (id) => {
    try {
      const { data } = await axios.get(`${API_URL}/stories/series/${id}`)
      if (data.success) {
        setSeriesData(data)
        const part = data.parts?.find(p => p.part === currentPartNumber)
        if (part) {
          setCurrentPart(part)
          loadPartIntoGenerator(part)
        } else {
          setCurrentPart(null)
        }
      }
    } catch (error) {
      console.error('Failed to load series:', error)
      setError('Failed to load series: ' + error.message)
    }
  }

  const loadPartIntoGenerator = (part) => {
    // ✅ Load story with title
    if (part.story_text) {
      setStoryData({
        story: part.story_text,
        word_count: part.word_count,
        estimated_duration: part.duration,
        title: part.title || 'Untitled'  // ✅ Add title
      })
      setEditStory(part.story_text)
      setStep(1)
    }

    // ✅ Load audio
    if (part.audio_path) {
      setAudioData({
        audio_path: part.audio_path,
        duration: part.duration
      })
      if (step < 2) setStep(2)
    }

    // ✅ Load subtitles (was missing!)
    if (part.subtitles && part.subtitles.length > 0) {
      setSubtitleData(part.subtitles)
      setEditSubtitles(part.subtitles)
      setTimingSource(part.timing_source || 'elevenlabs_api')
      if (step < 3) setStep(3)
    }

    // ✅ Load video
    if (part.video_path) {
      setVideoData({
        video_path: part.video_path
      })
      if (step < 5) setStep(5)
    }

    // ✅ Load effects if available
    if (part.effects && part.effects.length > 0) {
      setEffectTimeline(part.effects)
    }
  }

  const loadSeriesAndContinue = async (id) => {
    try {
      const { data } = await axios.get(`${API_URL}/stories/series/${id}`)
      if (data.success) {
        setSeriesId(id)
        setSelectedGenre(data.genre)
        setSeriesData(data)

        // ✅ Load the current part (the one that was clicked in Library)
        const currentPart = data.parts?.find(p => p.part === data.current_part)

        if (currentPart) {
          // ✅ Actually load the part data (story, audio, video, subtitles, effects)
          loadPartIntoGenerator(currentPart)
        } else {
          // No data yet - reset to step 0
          setStep(0)
        }
      }
    } catch (error) {
      console.error('Failed to load series:', error)
      setError('Failed to load series: ' + error.message)
    }
  }

  const handleLoadPart = async (partNum) => {
    // First update the part number
    setCurrentPartNumber(partNum)

    // Check if this part exists in series data
    const existingPart = seriesData?.parts?.find(p => p.part === partNum)

    if (existingPart) {
      // Load existing part data
      loadPartIntoGenerator(existingPart)
    } else {
      // New part - reset everything to empty
      setStoryData(null)
      setAudioData(null)
      setSubtitleData(null)
      setVideoData(null)
      setTimingSource(null)
      setEffectTimeline([])
      setEditStory('')
      setEditSubtitles([])
      setStep(0)
    }
  }

  const handleAddPart = async () => {
    try {
      setLoading(true)
      await axios.patch(`${API_URL}/series/${seriesId}`, {
        total_parts: seriesData.total_parts + 1
      })

      // Reset all workflow state for new part
      setStoryData(null)
      setAudioData(null)
      setSubtitleData(null)
      setVideoData(null)
      setTimingSource(null)
      setEffectTimeline([])
      setEditStory('')
      setEditSubtitles([])
      setStep(0)

      await loadSeriesData(seriesId)
      setCurrentPartNumber(seriesData.total_parts + 1)
    } catch (error) {
      console.error('Failed to add part:', error)
      setError('Failed to add part: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const loadPreviousPartContext = () => {
    if (currentPartNumber > 1 && seriesData?.parts) {
      const previousPart = seriesData.parts.find(p => p.part === currentPartNumber - 1)
      if (previousPart && previousPart.story_text) {
        setEditStory(previousPart.story_text)
        setError('')
      }
    }
  }

  const handleAddNextPart = async () => {
    if (operationInProgress) {
      setError('Another operation is already in progress. Please wait.')
      return
    }

    setOperationInProgress('series')
    setLoading(true)
    try {
      // Increment total_parts
      await axios.patch(`${API_URL}/series/${seriesId}`, {
        total_parts: totalParts + 1
      })
      setTotalParts(prev => prev + 1)

      // Generate next part
      const { data } = await axios.post(
        `${API_URL}/stories/series/${seriesId}/next-part`,
        { target_duration: targetDuration }
      )

      if (data.success) {
        setStoryData({
          story: data.story_text,
          word_count: data.part_metadata.word_count,
          hook: data.part_metadata.hook,
          estimated_duration: data.duration
        })
        setEditStory(data.story_text)
        setCurrentPartNumber(data.part_number)

        // Reset workflow
        setAudioData(null)
        setSubtitleData(null)
        setVideoData(null)
        setTimingSource(null)
        setEffectTimeline(null)
        setStep(1)
      }
    } catch (error) {
      console.error('Failed to add next part:', error)
      setError('Failed to add next part: ' + error.message)
    } finally {
      setLoading(false)
      setOperationInProgress(null)
    }
  }

  const handleReset = () => {
    setStep(0)
    setStoryData(null)
    setAudioData(null)
    setSubtitleData(null)
    setVideoData(null)
    setTimingSource(null)
    setEditStory('')
    setEditSubtitles([])
    setEffectPrompt('')
    setEffectTimeline([])
    setError('')
    setSeriesMode(false)
    setSeriesId(null)
    setSeriesTheme('')
    setTotalParts(3)
    setCurrentPartNumber(1)
    setSeriesData(null)
    setCurrentPart(null)
    clearSavedState() // Clear persistence on manual reset
  }

  const handleGoBack = () => {
    if (step > 0) {
      setStep(step - 1)
      setError('')
    }
  }

  const handleDeleteAudio = () => {
    setAudioData(null)
    setSubtitleData(null)
    setEditSubtitles([])
    setTimingSource(null)
    setStep(1)
  }

  const handleDeleteSubtitles = () => {
    setSubtitleData(null)
    setEditSubtitles([])
    setTimingSource(null)
    setStep(2)
  }

  const handleDeleteVideo = () => {
    setVideoData(null)
    setStep(3)
  }

  const handleRegenerateStory = async () => {
    setStoryData(null)
    setEditStory('')
    await handleGenerateStory()
  }

  const handleRegenerateAudio = async () => {
    setAudioData(null)
    await handleGenerateAudio()
  }

  const handleRegenerateSubtitles = async () => {
    setSubtitleData(null)
    setEditSubtitles([])
    await handleGenerateSubtitles()
  }

  const handleGenerateEffects = async () => {
    if (operationInProgress) {
      setError('Another operation is already in progress. Please wait.')
      return
    }

    if (!effectPrompt.trim()) {
      setError('Please enter an effect prompt')
      return
    }

    setOperationInProgress('effects')
    setError('')

    try {
      const { data } = await axios.post(`${API_URL}/effects/generate`, {
        prompt: effectPrompt,
        story_text: editStory,
        audio_duration: audioData?.duration || 60.0,
        subtitles: editSubtitles
      })

      if (data.success) {
        setEffectTimeline(data.timeline)
        console.log('Generated effects:', data.timeline)
      }
    } catch (error) {
      setError('Failed to generate effects: ' + (error.response?.data?.error || error.message))
    } finally {
      setOperationInProgress(null)
    }
  }

  const handleClearEffects = () => {
    setEffectPrompt('')
    setEffectTimeline([])
  }

  const handleUpdateEffect = (effectId, updatedEffect) => {
    setEffectTimeline(prev =>
      prev.map(effect => effect.id === effectId ? updatedEffect : effect)
    )
  }

  const handleDeleteEffect = (effectId) => {
    setEffectTimeline(prev =>
      prev.filter(effect => effect.id !== effectId)
    )
  }

  const handleAddEffect = (newEffect) => {
    setEffectTimeline(prev => [...prev, newEffect])
  }

  const handleManualStory = () => {
    if (editStory.trim().length === 0) {
      setError('Please write a story before continuing')
      return
    }
    const wordCount = editStory.trim().split(/\s+/).filter(w => w.length > 0).length
    if (wordCount < 50) {
      setError('Story too short. Aim for 100+ words for best results')
      return
    }

    setStoryData({
      story: editStory,
      word_count: wordCount,
      estimated_duration: Math.ceil(wordCount / 2.5)
    })
    setStep(1)
  }

  const handleImproveStory = async () => {
    if (operationInProgress) {
      setError('Another operation is already in progress. Please wait.')
      return
    }

    setOperationInProgress('improve')
    setError('')

    setStoryHistory([...storyHistory, editStory])

    try {
      const { data } = await axios.post(`${API_URL}/stories/improve`, {
        current_text: editStory,
        improvement_type: 'enhance',
        genre: selectedGenre,
        target_duration: targetDuration,
        custom_instructions: improvePrompt,
        series_id: seriesId,
        part_number: currentPartNumber
      })

      if (data.success) {
        setEditStory(data.improved_text)
        setStoryData({
          ...storyData,
          story: data.improved_text,
          word_count: data.word_count,
          estimated_duration: data.estimated_duration
        })
        setShowImproveModal(false)
        setImprovePrompt('')
      }
    } catch (error) {
      setError('Failed to improve story: ' + (error.response?.data?.error || error.message))
      if (storyHistory.length > 0) {
        setEditStory(storyHistory[storyHistory.length - 1])
        setStoryHistory(storyHistory.slice(0, -1))
      }
    } finally {
      setOperationInProgress(null)
    }
  }

  const handleUndo = () => {
    if (storyHistory.length > 0) {
      const previous = storyHistory[storyHistory.length - 1]
      setEditStory(previous)
      const wordCount = previous.trim().split(/\s+/).filter(w => w.length > 0).length
      setStoryData({
        ...storyData,
        story: previous,
        word_count: wordCount,
        estimated_duration: Math.ceil(wordCount / 2.5)
      })
      setStoryHistory(storyHistory.slice(0, -1))
    }
  }

  const handleProceedFromImproveMode = async () => {
    if (editStory.trim().length === 0) {
      setError('Please paste or write a story to improve')
      return
    }
    const wordCount = editStory.trim().split(/\s+/).filter(w => w.length > 0).length
    if (wordCount < 50) {
      setError('Story too short. Aim for 100+ words for best results')
      return
    }

    setStoryData({
      story: editStory,
      word_count: wordCount,
      estimated_duration: Math.ceil(wordCount / 2.5)
    })
    setShowImproveModal(true)
  }

  return (
    <div className="p-8">
      {/* Recovery Notification */}
      {showRecovery && recoveredState && (
        <RecoveryNotification
          state={recoveredState}
          onResume={handleRecoveryResume}
          onDismiss={handleRecoveryDismiss}
        />
      )}

      {/* Improve Modal */}
      <ImproveModal
        show={showImproveModal}
        onClose={() => setShowImproveModal(false)}
        onImprove={handleImproveStory}
        customInstructions={improvePrompt}
        setCustomInstructions={setImprovePrompt}
        loading={operationInProgress === 'improve'}
      />

      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Video Generator</h1>
        <p className="text-gray-400">Simple step-by-step viral video creation</p>
      </div>

      {/* Story Title - Clean & Minimal */}
      {step >= 1 && storyData?.title && (
        <div className="mb-4 pb-3 border-b border-dark-border">
          <h2 className="text-xl font-semibold text-white">
            {storyData.title}
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            {selectedGenre.replace('_', ' ').toUpperCase()} • {storyData.estimated_duration || 60}s
          </p>
        </div>
      )}

      {/* Global Loading Indicator */}
      {operationInProgress && (
        <div className="mb-6 card bg-primary-900 bg-opacity-20 border-primary-800">
          <div className="flex items-center gap-3">
            <Loader size={20} className="animate-spin text-primary-400" />
            <div>
              <p className="font-medium text-primary-400">
                {operationInProgress === 'story' && 'Generating Story...'}
                {operationInProgress === 'audio' && 'Generating Audio...'}
                {operationInProgress === 'subtitles' && 'Generating Subtitles...'}
                {operationInProgress === 'effects' && 'Generating Effects...'}
                {operationInProgress === 'video' && 'Creating Video...'}
                {operationInProgress === 'improve' && 'Improving Story...'}
                {operationInProgress === 'series' && 'Processing Series...'}
              </p>
              <p className="text-sm text-primary-300 mt-1">Please wait, this may take a moment</p>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 card bg-red-900 bg-opacity-20 border-red-800">
          <div className="flex items-start gap-3">
            <AlertCircle size={20} className="text-red-400 mt-0.5" />
            <div>
              <p className="font-medium text-red-400">Error</p>
              <p className="text-sm text-red-300 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-6">
        {/* Settings Panel */}
        <div className="col-span-1 space-y-4">
          <div className="card">
            <h3 className="font-bold mb-4">Settings</h3>


            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Genre</label>
              <select
                value={selectedGenre}
                onChange={(e) => setSelectedGenre(e.target.value)}
                className="input w-full"
                disabled={step > 0}
              >
                {genres.map(genre => (
                  <option key={genre} value={genre}>
                    {GENRE_LABELS[genre] || genre}
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Background</label>
              <select
                value={selectedBackground}
                onChange={(e) => setSelectedBackground(e.target.value)}
                className="input w-full"
              >
                <option value="">Random</option>
                {backgrounds.map(bg => (
                  <option key={bg} value={bg}>{bg}</option>
                ))}
              </select>
            </div>

            {useElevenLabs && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Voice (ElevenLabs)</label>
                <select
                  value={selectedVoice}
                  onChange={(e) => setSelectedVoice(e.target.value)}
                  className="input w-full"
                  disabled={step > 1}
                >
                  {VOICES.map(voice => (
                    <option key={voice.id} value={voice.id}>
                      {voice.name} - {voice.desc}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Words per subtitle: {wordsPerChunk} {wordsPerChunk >= 3 && wordsPerChunk <= 5 ? '✓ Optimal' : ''}
              </label>
              <input
                type="range"
                min="2"
                max="6"
                value={wordsPerChunk}
                onChange={(e) => setWordsPerChunk(parseInt(e.target.value))}
                className="w-full"
                disabled={step > 2}
              />
              <p className="text-xs text-gray-400 mt-1">3-5 words = best for 2025 retention</p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Target Duration: {targetDuration}s {targetDuration >= 60 && targetDuration <= 90 ? '✓ Monetizable' : targetDuration < 60 ? '⚠️ Too short' : '⚠️ Too long'}
              </label>
              <input
                type="range"
                min="5"
                max="90"
                step="5"
                value={targetDuration}
                onChange={(e) => setTargetDuration(parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-gray-400 mt-1">60-90s = Creator Rewards sweet spot</p>
            </div>

            <div className="mb-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={useElevenLabs}
                  onChange={(e) => setUseElevenLabs(e.target.checked)}
                  disabled={step > 1}
                />
                <span className="text-sm">Use ElevenLabs TTS (Premium)</span>
              </label>
            </div>

            {step >= 5 && (
              <button onClick={handleReset} className="btn-secondary w-full">
                Start New Video
              </button>
            )}
          </div>
        </div>

        {/* Main Panel */}
        <div className="col-span-2 space-y-6">

          {/* Step 0: Start */}
          {step === 0 && (
            <div className={`card ${seriesMode ? 'border-2 border-purple-700 bg-purple-900 bg-opacity-10' : ''}`}>
              <StoryModeSelector
                mode={storyMode}
                onModeChange={setStoryMode}
                disabled={loading}
              />

              {storyMode === 'generate' && (
                <div className="text-center py-12">
                  <h2 className="text-2xl font-bold mb-2">
                    {seriesMode ? 'Create Story Series' : 'Ready to Create?'}
                  </h2>
                  <p className="text-gray-400 mb-6">
                    {seriesMode
                      ? `Create a ${totalParts}-part story series about "${seriesTheme || 'your topic'}"`
                      : 'Click below to generate your first viral story'}
                  </p>
                  {seriesMode && !seriesTheme && (
                    <p className="text-red-400 text-sm mb-4">Please enter a series theme first</p>
                  )}
                  <button
                    onClick={seriesMode ? handleCreateSeries : handleGenerateStory}
                    disabled={operationInProgress !== null || (seriesMode && !seriesTheme)}
                    className="btn-primary inline-flex items-center gap-2"
                  >
                    {operationInProgress === 'series' || operationInProgress === 'story' ? (
                      <>
                        <Loader size={20} className="animate-spin" />
                        {seriesMode ? 'Creating Series...' : 'Generating Story...'}
                      </>
                    ) : (
                      <>
                        <Play size={20} />
                        {seriesMode ? 'Create Series' : 'Generate Story'}
                      </>
                    )}
                  </button>
                </div>
              )}

              {storyMode === 'write' && (
                <ManualStoryInput
                  value={editStory}
                  onChange={setEditStory}
                  onContinue={handleManualStory}
                  loading={loading}
                />
              )}

              {storyMode === 'improve' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-gray-300">
                      Paste Story to Improve
                    </label>
                    <textarea
                      value={editStory}
                      onChange={(e) => setEditStory(e.target.value)}
                      placeholder="Paste your existing story here...&#10;&#10;Then click 'Improve Story' to enhance it with AI"
                      className="input w-full h-48 md:h-64 resize-none font-mono text-sm"
                      disabled={loading}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-400">
                      {editStory.trim().split(/\s+/).filter(w => w.length > 0).length} words
                      <span className="mx-2">•</span>
                      ~{Math.ceil(editStory.trim().split(/\s+/).filter(w => w.length > 0).length / 2.5)}s duration
                    </div>

                    <button
                      onClick={handleProceedFromImproveMode}
                      disabled={loading || editStory.trim().length === 0}
                      className={`btn-primary flex items-center gap-2 ${editStory.trim().length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <Sparkles size={16} />
                      Improve Story
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}


          {/* Step 1: Story */}
          {step >= 1 && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold">Story</h3>
                <div className="flex gap-2 flex-wrap">
                  {step === 1 && (
                    <>
                      <button
                        onClick={handleGoBack}
                        className="btn-secondary flex items-center gap-2"
                        disabled={operationInProgress !== null}
                      >
                        <ArrowLeft size={16} />
                        Back
                      </button>
                      {storyHistory.length > 0 && (
                        <button
                          onClick={handleUndo}
                          className="btn-secondary text-xs flex items-center gap-1"
                          disabled={operationInProgress !== null}
                        >
                          <Undo2 size={14} />
                          Undo
                        </button>
                      )}
                      <button
                        onClick={() => setShowImproveModal(true)}
                        className="btn-secondary flex items-center gap-2"
                        disabled={operationInProgress !== null}
                      >
                        <Sparkles size={16} />
                        Improve
                      </button>
                      <button
                        onClick={handleRegenerateStory}
                        className="btn-secondary flex items-center gap-2"
                        disabled={operationInProgress !== null}
                      >
                        {operationInProgress === 'story' ? (
                          <>
                            <Loader size={16} className="animate-spin" />
                            Regenerating...
                          </>
                        ) : (
                          <>
                            <RefreshCw size={16} />
                            Regenerate
                          </>
                        )}
                      </button>
                      <button
                        onClick={handleGenerateAudio}
                        className="btn-primary flex items-center gap-2"
                        disabled={operationInProgress !== null}
                      >
                        {operationInProgress === 'audio' ? (
                          <>
                            <Loader size={16} className="animate-spin" />
                            Generating Audio...
                          </>
                        ) : (
                          <>
                            <CheckCircle size={16} />
                            Generate Audio
                          </>
                        )}
                      </button>
                    </>
                  )}
                </div>
              </div>
              <textarea
                value={editStory}
                onChange={(e) => setEditStory(e.target.value)}
                className="input w-full h-32 resize-none font-mono text-sm"
                disabled={step > 1 || operationInProgress !== null}
              />
              <p className="text-sm text-gray-400 mt-2">
                {editStory.split(' ').length} words • ~{Math.ceil(editStory.split(' ').length / 2.5)}s
                {operationInProgress === 'improve' && <span className="text-primary-500 ml-2">• Improving...</span>}
              </p>
            </div>
          )}

          {/* Step 2: Audio */}
          {step >= 2 && audioData && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <h3 className="font-bold">Audio Preview</h3>
                  {subtitleData && subtitleData.length > 0 && (
                    <span className="inline-block px-2 py-1 text-xs font-medium bg-primary-900 bg-opacity-50 text-primary-300 rounded border border-primary-700">
                      Subtitles Ready
                    </span>
                  )}
                </div>
                {step === 2 && (
                  <div className="flex gap-2">
                    <button
                      onClick={handleGoBack}
                      className="btn-secondary flex items-center gap-2"
                      disabled={operationInProgress !== null}
                    >
                      <ArrowLeft size={16} />
                      Back
                    </button>
                    <button
                      onClick={handleDeleteAudio}
                      className="btn-secondary flex items-center gap-2 text-red-400 hover:bg-red-900"
                      disabled={operationInProgress !== null}
                    >
                      <Trash2 size={16} />
                      Delete
                    </button>
                    <button
                      onClick={handleRegenerateAudio}
                      className="btn-secondary flex items-center gap-2"
                      disabled={operationInProgress !== null}
                    >
                      {operationInProgress === 'audio' ? (
                        <>
                          <Loader size={16} className="animate-spin" />
                          Regenerating...
                        </>
                      ) : (
                        <>
                          <RefreshCw size={16} />
                          Regenerate
                        </>
                      )}
                    </button>
                    {subtitleData && subtitleData.length > 0 ? (
                      <button
                        onClick={() => setStep(3)}
                        className="btn-primary flex items-center gap-2"
                        disabled={operationInProgress !== null}
                      >
                        <CheckCircle size={16} />
                        View Subtitles
                      </button>
                    ) : (
                      <button
                        onClick={handleGenerateSubtitles}
                        className="btn-primary flex items-center gap-2"
                        disabled={operationInProgress !== null}
                      >
                        {operationInProgress === 'subtitles' ? (
                          <>
                            <Loader size={16} className="animate-spin" />
                            Generating Subtitles...
                          </>
                        ) : (
                          <>
                            <CheckCircle size={16} />
                            Generate Subtitles
                          </>
                        )}
                      </button>
                    )}
                  </div>
                )}
              </div>
              <AudioPlayer
                src={`${API_URL}/files/audio/${audioData.audio_path.split(/[\\/]/).pop()}`}
              />
              <p className="text-sm text-gray-400 mt-2">
                Duration: {audioData.duration?.toFixed(1)}s • Voice: {selectedVoice}
              </p>
              {audioData.audio_path && (
                <div className="mt-3 p-2 bg-dark-hover rounded text-xs">
                  <p className="text-gray-400 mb-1">File Path:</p>
                  <code
                    onClick={() => navigator.clipboard.writeText(audioData.audio_path)}
                    className="block text-mono font-mono text-gray-300 cursor-pointer hover:text-white hover:bg-dark-border p-1 rounded break-all select-all"
                    title="Click to copy"
                  >
                    {audioData.audio_path}
                  </code>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Subtitles */}
          {step >= 3 && subtitleData && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <h3 className="font-bold">Subtitles</h3>
                  {timingSource === 'elevenlabs_api' && (
                    <span className="inline-block px-2 py-1 text-xs font-medium bg-green-900 bg-opacity-50 text-green-300 rounded border border-green-700">
                      Perfect Sync
                    </span>
                  )}
                  {timingSource === 'linear_estimation' && (
                    <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-900 bg-opacity-50 text-blue-300 rounded border border-blue-700">
                      Standard Sync
                    </span>
                  )}
                </div>
                {step === 3 && (
                  <div className="flex gap-2">
                    <button
                      onClick={handleGoBack}
                      className="btn-secondary flex items-center gap-2"
                      disabled={operationInProgress !== null}
                    >
                      <ArrowLeft size={16} />
                      Back
                    </button>
                    <button
                      onClick={handleDeleteSubtitles}
                      className="btn-secondary flex items-center gap-2 text-red-400 hover:bg-red-900"
                      disabled={operationInProgress !== null}
                    >
                      <Trash2 size={16} />
                      Delete
                    </button>
                    <button
                      onClick={handleRegenerateSubtitles}
                      className="btn-secondary flex items-center gap-2"
                      disabled={operationInProgress !== null}
                    >
                      {operationInProgress === 'subtitles' ? (
                        <>
                          <Loader size={16} className="animate-spin" />
                          Regenerating...
                        </>
                      ) : (
                        <>
                          <RefreshCw size={16} />
                          Regenerate
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {editSubtitles.map((sub, idx) => (
                  <div key={idx} className="flex items-center gap-3 bg-dark-hover p-2 rounded">
                    <span className="text-xs text-gray-500 w-20">
                      {sub.start.toFixed(1)}s - {sub.end.toFixed(1)}s
                    </span>
                    <input
                      type="text"
                      value={sub.text}
                      onChange={(e) => {
                        const newSubs = [...editSubtitles]
                        newSubs[idx].text = e.target.value
                        setEditSubtitles(newSubs)
                      }}
                      className="input flex-1 text-sm"
                      disabled={step > 3 || operationInProgress !== null}
                    />
                  </div>
                ))}
              </div>
              <p className="text-sm text-gray-400 mt-2">
                {editSubtitles.length} subtitle chunks
              </p>
            </div>
          )}

          {/* AI Effects (Optional) */}
          {step === 3 && (
            <div className="card border-2 border-purple-800 bg-purple-900 bg-opacity-10">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-bold text-purple-300">Effects</h3>
                  <p className="text-xs text-purple-400 mt-1">
                    Use AI to generate effects or add them manually
                  </p>
                </div>
                {effectTimeline.length > 0 && (
                  <button
                    onClick={handleClearEffects}
                    className="btn-secondary text-xs"
                    disabled={operationInProgress !== null}
                  >
                    Clear All Effects
                  </button>
                )}
              </div>

              {/* AI Effect Generator */}
              <div className="mb-4 p-3 bg-dark-card rounded border border-purple-700">
                <p className="text-xs font-medium text-purple-300 mb-2">AI Effect Generator</p>
                <div className="mb-2">
                  <textarea
                    value={effectPrompt}
                    onChange={(e) => setEffectPrompt(e.target.value)}
                    placeholder="Example: 'Add zoom effects on emphasis words' or 'Make the climax dramatic with red subtitles'"
                    className="input w-full h-16 resize-none text-sm"
                    disabled={operationInProgress !== null}
                  />
                </div>
                <button
                  onClick={handleGenerateEffects}
                  className="btn-secondary text-sm flex items-center gap-2 w-full"
                  disabled={operationInProgress !== null || !effectPrompt.trim()}
                >
                  {operationInProgress === 'effects' ? (
                    <>
                      <Loader size={16} className="animate-spin" />
                      Generating Effects...
                    </>
                  ) : (
                    <>
                      <Play size={16} />
                      Generate from Prompt
                    </>
                  )}
                </button>
              </div>

              {/* Effect Inspector */}
              <EffectInspector
                effectTimeline={effectTimeline}
                onUpdateEffect={handleUpdateEffect}
                onDeleteEffect={handleDeleteEffect}
                onAddEffect={handleAddEffect}
                audioDuration={audioData?.duration || 60}
                disabled={operationInProgress !== null}
              />

              {/* Create Video Button */}
              <div className="mt-4">
                <button
                  onClick={handleCreateVideo}
                  className="btn-primary flex items-center gap-2 w-full"
                  disabled={operationInProgress !== null}
                >
                  {operationInProgress === 'video' ? (
                    <>
                      <Loader size={16} className="animate-spin" />
                      Creating Video...
                    </>
                  ) : (
                    <>
                      <Play size={16} />
                      Create Video {effectTimeline.length > 0 ? `(${effectTimeline.length} effects)` : ''}
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Rendering */}
          {step === 4 && loading && (
            <div className="card text-center py-12">
              <Loader size={48} className="animate-spin mx-auto mb-4 text-primary-500" />
              <h3 className="text-xl font-bold mb-2">Creating Video...</h3>
              <p className="text-gray-400">This may take a minute</p>
            </div>
          )}

          {/* Step 5: Complete */}
          {step >= 5 && videoData && (
            <div className="card bg-green-900 bg-opacity-20 border-green-800">
              <div className="flex items-start gap-3 mb-4">
                <CheckCircle size={24} className="text-green-400" />
                <div>
                  <h3 className="font-bold text-green-400">Video Generated!</h3>
                  <p className="text-sm text-green-300 mt-1">Your video is ready</p>
                </div>
              </div>

              <div style={{ maxHeight: '400px', overflow: 'hidden', borderRadius: '0.5rem', marginBottom: '1rem' }}>
                <VideoPlayer
                  src={`${API_URL}/files/video/${videoData.video_path.split(/[\\/]/).pop()}`}
                  className="w-full"
                />
              </div>

              {videoData.video_path && (
                <div className="mb-4 p-2 bg-dark-hover rounded text-xs">
                  <p className="text-gray-400 mb-1">File Path:</p>
                  <code
                    onClick={() => navigator.clipboard.writeText(videoData.video_path)}
                    className="block text-mono font-mono text-gray-300 cursor-pointer hover:text-white hover:bg-dark-border p-1 rounded break-all select-all"
                    title="Click to copy"
                  >
                    {videoData.video_path}
                  </code>
                </div>
              )}

              <div className="flex gap-2">
                <button
                  onClick={handleGoBack}
                  className="btn-secondary flex items-center gap-2"
                >
                  <ArrowLeft size={16} />
                  Back
                </button>
                <button
                  onClick={handleDeleteVideo}
                  className="btn-secondary flex items-center gap-2 text-red-400 hover:bg-red-900"
                >
                  <Trash2 size={16} />
                  Delete & Retry
                </button>
                <a
                  href={`${API_URL}/files/video/${videoData.video_path.split(/[\\/]/).pop()}`}
                  download
                  className="btn-primary flex items-center gap-2"
                >
                  <Download size={20} />
                  Download Video
                </a>
                <button onClick={handleReset} className="btn-secondary flex items-center gap-2">
                  <RefreshCw size={16} />
                  Create Another
                </button>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  )
}
