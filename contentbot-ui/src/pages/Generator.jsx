import { useState, useEffect } from 'react'
import { Play, Download, Loader, CheckCircle, AlertCircle, Edit2, Check, X } from 'lucide-react'
import axios from 'axios'
import AudioPlayer from '../components/AudioPlayer'
import VideoPlayer from '../components/VideoPlayer'

const API_URL = 'http://localhost:5000/api'

const VOICES = [
  { id: 'mark', name: 'Mark', desc: 'Friendly narrator' },
  { id: 'emily', name: 'Emily', desc: 'Professional female' },
  { id: 'josh', name: 'Josh', desc: 'Energetic male' },
  { id: 'bella', name: 'Bella', desc: 'Warm female' },
]

export default function Generator() {
  const [genres, setGenres] = useState([])
  const [backgrounds, setBackgrounds] = useState([])

  const [selectedGenre, setSelectedGenre] = useState('comedy')
  const [selectedBackground, setSelectedBackground] = useState('')
  const [selectedVoice, setSelectedVoice] = useState('mark')
  const [wordsPerChunk, setWordsPerChunk] = useState(2)
  const [targetDuration, setTargetDuration] = useState(60)
  const [useElevenLabs, setUseElevenLabs] = useState(false)

  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [storyData, setStoryData] = useState(null)
  const [audioData, setAudioData] = useState(null)
  const [subtitleData, setSubtitleData] = useState(null)
  const [videoData, setVideoData] = useState(null)

  const [editStory, setEditStory] = useState('')
  const [editSubtitles, setEditSubtitles] = useState([])

  useEffect(() => {
    loadConfig()
  }, [])

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
  }

  return (
    <div className="p-8">
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
                  <option key={genre} value={genre}>{genre}</option>
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

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Voice</label>
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

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Words per subtitle: {wordsPerChunk}
              </label>
              <input
                type="range"
                min="1"
                max="4"
                value={wordsPerChunk}
                onChange={(e) => setWordsPerChunk(parseInt(e.target.value))}
                className="w-full"
                disabled={step > 2}
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">
                Target Duration (seconds): {targetDuration}
              </label>
              <input
                type="range"
                min="15"
                max="180"
                step="5"
                value={targetDuration}
                onChange={(e) => setTargetDuration(parseInt(e.target.value))}
                className="w-full"
              />
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
                  {step === 1 && !loading && (
                    <button
                      onClick={handleGenerateAudio}
                      className="btn-primary flex items-center gap-2"
                    >
                      <CheckCircle size={16} />
                      Looks Good - Generate Audio
                    </button>
                  )}
                </div>
              </div>
              <textarea
                value={editStory}
                onChange={(e) => setEditStory(e.target.value)}
                className="input w-full h-32 resize-none font-mono text-sm"
                disabled={step > 1}
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
                {step === 2 && !loading && (
                  <button
                    onClick={handleGenerateSubtitles}
                    className="btn-primary flex items-center gap-2"
                  >
                    <CheckCircle size={16} />
                    Next - Generate Subtitles
                  </button>
                )}
              </div>
              <AudioPlayer
                src={`${API_URL}/files/audio/${audioData.audio_path.split('/').pop()}`}
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
                {step === 3 && !loading && (
                  <button
                    onClick={handleCreateVideo}
                    className="btn-primary flex items-center gap-2"
                  >
                    {loading ? <Loader size={16} className="animate-spin" /> : <Play size={16} />}
                    Create Video
                  </button>
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
                      disabled={step > 3}
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
                <a
                  href={`${API_URL}/files/video/${videoData.video_path.split(/[\\/]/).pop()}`}
                  download
                  className="btn-primary flex items-center gap-2"
                >
                  <Download size={20} />
                  Download Video
                </a>
                <button onClick={handleReset} className="btn-secondary">
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
