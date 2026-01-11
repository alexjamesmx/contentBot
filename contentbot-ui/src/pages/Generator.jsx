import { useState, useEffect, useMemo } from 'react'
import { Play, Download, Loader, CheckCircle, AlertCircle, Edit2, Check, X, ArrowLeft, Trash2, RefreshCw } from 'lucide-react'
import axios from 'axios'
import AudioPlayer from '../components/AudioPlayer'
import VideoPlayer from '../components/VideoPlayer'
import RecoveryNotification from '../components/RecoveryNotification'
import { useGeneratorPersistence, checkActiveJobs, pollActiveJobs } from '../hooks/useGeneratorPersistence'

const API_URL = 'http://localhost:5000/api'

const VOICES = [
  { id: 'mark', name: 'Mark', desc: 'Storytelling, casual TikToks' },
  { id: 'snap', name: 'Snap', desc: 'Playful, Gen-Z, memes' },
  { id: 'peter', name: 'Peter', desc: 'Bold narrator, trending' },
  { id: 'viraj', name: 'Viraj', desc: 'Warm, passionate, expressive' },
  { id: 'rachel', name: 'Rachel', desc: 'Clear, professional' },
  { id: 'adam', name: 'Adam', desc: 'Deep, authoritative' },
]

const GENRE_LABELS = {
  'comedy': 'Gen-Z Comedy',
  'terror': 'Creepy Horror',
  'aita': 'AITA Drama',
  'genz_chaos': 'Unhinged Chaos',
  'relationship_drama': 'Relationship Tea'
}

export default function Generator({ reusedContent, onClearReused }) {
  const [genres, setGenres] = useState(['comedy', 'terror', 'aita', 'genz_chaos', 'relationship_drama'])
  const [backgrounds, setBackgrounds] = useState([])

  const [selectedGenre, setSelectedGenre] = useState('comedy')
  const [selectedBackground, setSelectedBackground] = useState('')
  const [selectedVoice, setSelectedVoice] = useState('mark')
  const [wordsPerChunk, setWordsPerChunk] = useState(4)
  const [targetDuration, setTargetDuration] = useState(75)
  const [useElevenLabs, setUseElevenLabs] = useState(true)

  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [storyData, setStoryData] = useState(null)
  const [audioData, setAudioData] = useState(null)
  const [subtitleData, setSubtitleData] = useState(null)
  const [videoData, setVideoData] = useState(null)

  const [editStory, setEditStory] = useState('')
  const [editSubtitles, setEditSubtitles] = useState([])

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
    editStory, editSubtitles,
    selectedGenre, selectedBackground, selectedVoice,
    wordsPerChunk, targetDuration, useElevenLabs
  }), [step, storyData, audioData, subtitleData, videoData, editStory, editSubtitles,
      selectedGenre, selectedBackground, selectedVoice, wordsPerChunk, targetDuration, useElevenLabs])

  // State setter for bulk updates from persistence
  const setPersistedState = (saved) => {
    if (saved.step !== undefined) setStep(saved.step)
    if (saved.storyData) setStoryData(saved.storyData)
    if (saved.audioData) setAudioData(saved.audioData)
    if (saved.subtitleData) setSubtitleData(saved.subtitleData)
    if (saved.videoData) setVideoData(saved.videoData)
    if (saved.editStory) setEditStory(saved.editStory)
    if (saved.editSubtitles) setEditSubtitles(saved.editSubtitles)
    if (saved.selectedGenre) setSelectedGenre(saved.selectedGenre)
    if (saved.selectedBackground) setSelectedBackground(saved.selectedBackground)
    if (saved.selectedVoice) setSelectedVoice(saved.selectedVoice)
    if (saved.wordsPerChunk) setWordsPerChunk(saved.wordsPerChunk)
    if (saved.targetDuration) setTargetDuration(saved.targetDuration)
    if (saved.useElevenLabs !== undefined) setUseElevenLabs(saved.useElevenLabs)
  }

  // Enable persistence
  const { clearSavedState, hasSavedState } = useGeneratorPersistence(persistentState, setPersistedState)

  useEffect(() => {
    loadConfig()
    initializeRecovery()
  }, [])

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

  const handleGenerateStory = async () => {
    setLoading(true)
    setError('')
    setStep(1)

    try {
      const { data } = await axios.post(`${API_URL}/generate/story`, {
        genre: selectedGenre,
        target_duration: targetDuration
      })

      if (data.success) {
        setStoryData(data.story)
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
    }
  }

  const handleGenerateAudio = async () => {
    setLoading(true)
    setError('')

    try {
      const { data } = await axios.post(`${API_URL}/generate/audio`, {
        text: editStory,
        voice: selectedVoice,
        use_elevenlabs: useElevenLabs
      })

      if (data.success) {
        setAudioData(data)
        setStep(2)
        if (data.job_id) {
          setActiveJobIds(prev => ({ ...prev, audio: data.job_id }))
        }
      }
    } catch (error) {
      setError('Failed to generate audio: ' + (error.response?.data?.error || error.message))
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateSubtitles = async () => {
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
    }
  }

  const handleCreateVideo = async () => {
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
        background_video: selectedBackground || null
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
    }
  }

  const handleReset = () => {
    setStep(0)
    setStoryData(null)
    setAudioData(null)
    setSubtitleData(null)
    setVideoData(null)
    setEditStory('')
    setEditSubtitles([])
    setError('')
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
    setStep(1)
  }

  const handleDeleteSubtitles = () => {
    setSubtitleData(null)
    setEditSubtitles([])
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

      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Video Generator</h1>
        <p className="text-gray-400">Simple step-by-step viral video creation</p>
      </div>

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
                min="30"
                max="180"
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
            <div className="card text-center py-12">
              <h2 className="text-2xl font-bold mb-4">Ready to Create?</h2>
              <p className="text-gray-400 mb-6">Click below to generate your first viral story</p>
              <button
                onClick={handleGenerateStory}
                disabled={loading}
                className="btn-primary inline-flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader size={20} className="animate-spin" />
                    Generating Story...
                  </>
                ) : (
                  <>
                    <Play size={20} />
                    Generate Story
                  </>
                )}
              </button>
            </div>
          )}


          {/* Step 1: Story */}
          {step >= 1 && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold">Story</h3>
                <div className="flex gap-2">
                  {step === 1 && (
                    <>
                      <button
                        onClick={handleGoBack}
                        className="btn-secondary flex items-center gap-2"
                        disabled={loading}
                      >
                        <ArrowLeft size={16} />
                        Back
                      </button>
                      <button
                        onClick={handleRegenerateStory}
                        className="btn-secondary flex items-center gap-2"
                        disabled={loading}
                      >
                        {loading ? <Loader size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                        Regenerate
                      </button>
                      <button
                        onClick={handleGenerateAudio}
                        className="btn-primary flex items-center gap-2"
                        disabled={loading}
                      >
                        {loading ? (
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
                disabled={step > 1 || loading}
              />
              <p className="text-sm text-gray-400 mt-2">
                {editStory.split(' ').length} words • ~{Math.ceil(editStory.split(' ').length / 2.5)}s
              </p>
            </div>
          )}

          {/* Step 2: Audio */}
          {step >= 2 && audioData && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold">Audio Preview</h3>
                {step === 2 && (
                  <div className="flex gap-2">
                    <button
                      onClick={handleGoBack}
                      className="btn-secondary flex items-center gap-2"
                      disabled={loading}
                    >
                      <ArrowLeft size={16} />
                      Back
                    </button>
                    <button
                      onClick={handleDeleteAudio}
                      className="btn-secondary flex items-center gap-2 text-red-400 hover:bg-red-900"
                      disabled={loading}
                    >
                      <Trash2 size={16} />
                      Delete
                    </button>
                    <button
                      onClick={handleRegenerateAudio}
                      className="btn-secondary flex items-center gap-2"
                      disabled={loading}
                    >
                      {loading ? <Loader size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                      Regenerate
                    </button>
                    <button
                      onClick={handleGenerateSubtitles}
                      className="btn-primary flex items-center gap-2"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <Loader size={16} className="animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <CheckCircle size={16} />
                          Generate Subtitles
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
              <AudioPlayer
                src={`${API_URL}/files/audio/${audioData.audio_path.split(/[\\/]/).pop()}`}
              />
              <p className="text-sm text-gray-400 mt-2">
                Duration: {audioData.duration?.toFixed(1)}s • Voice: {selectedVoice}
              </p>
            </div>
          )}

          {/* Step 3: Subtitles */}
          {step >= 3 && subtitleData && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold">Subtitles</h3>
                {step === 3 && (
                  <div className="flex gap-2">
                    <button
                      onClick={handleGoBack}
                      className="btn-secondary flex items-center gap-2"
                      disabled={loading}
                    >
                      <ArrowLeft size={16} />
                      Back
                    </button>
                    <button
                      onClick={handleDeleteSubtitles}
                      className="btn-secondary flex items-center gap-2 text-red-400 hover:bg-red-900"
                      disabled={loading}
                    >
                      <Trash2 size={16} />
                      Delete
                    </button>
                    <button
                      onClick={handleRegenerateSubtitles}
                      className="btn-secondary flex items-center gap-2"
                      disabled={loading}
                    >
                      {loading ? <Loader size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                      Regenerate
                    </button>
                    <button
                      onClick={handleCreateVideo}
                      className="btn-primary flex items-center gap-2"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <Loader size={16} className="animate-spin" />
                          Creating Video...
                        </>
                      ) : (
                        <>
                          <Play size={16} />
                          Create Video
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
                      disabled={step > 3 || loading}
                    />
                  </div>
                ))}
              </div>
              <p className="text-sm text-gray-400 mt-2">
                {editSubtitles.length} subtitle chunks
              </p>
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

              <VideoPlayer
                src={`${API_URL}/files/video/${videoData.video_path.split(/[\\/]/).pop()}`}
                className="rounded-lg mb-4"
              />

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
