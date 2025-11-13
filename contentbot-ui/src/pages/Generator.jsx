import { useState, useEffect } from 'react'
import { Play, Download, Loader, CheckCircle, AlertCircle, Music, Eye, FolderOpen } from 'lucide-react'
import axios from 'axios'
import AudioPlayer from '../components/AudioPlayer'
import VideoPlayer from '../components/VideoPlayer'

export default function Generator() {
  const [genres, setGenres] = useState([])
  const [selectedGenre, setSelectedGenre] = useState('comedy')
  const [backgrounds, setBackgrounds] = useState([])
  const [selectedBackground, setSelectedBackground] = useState('')
  const [customStory, setCustomStory] = useState('')
  const [useCustomStory, setUseCustomStory] = useState(false)
  const [wordsPerChunk, setWordsPerChunk] = useState(2)
  const [useElevenLabs, setUseElevenLabs] = useState(false)
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(1)
  const [generatedData, setGeneratedData] = useState({})
  const [error, setError] = useState('')

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/config')
      if (response.data.success) {
        setGenres(response.data.config.genres)
        setBackgrounds(response.data.config.assets.backgrounds)
        // Keep ElevenLabs disabled by default (user can enable manually)
      }
    } catch (error) {
      console.error('Failed to load config:', error)
    }
  }

  const generateStory = async () => {
    setLoading(true)
    setError('')
    setStep(1)

    console.log('[STEP 1] Starting story generation...', { genre: selectedGenre, useCustomStory })

    try {
      const response = await axios.post('http://localhost:5000/api/generate/story', {
        genre: selectedGenre,
        custom_prompt: useCustomStory ? customStory : null
      })

      console.log('[STEP 1] Story generation response:', response.data)

      if (response.data.success) {
        console.log('[STEP 1] ✅ Story generated successfully!')
        setGeneratedData(prev => ({ ...prev, story: response.data.story }))
        setStep(2)
        await generateAudio(response.data.story.story)
      } else {
        throw new Error('Story generation returned success: false')
      }
    } catch (error) {
      console.error('[STEP 1] ❌ Story generation failed:', error)
      const errorMsg = 'Failed to generate story: ' + (error.response?.data?.error || error.message)
      setError(errorMsg)
      alert('❌ Error: ' + errorMsg)
      setLoading(false)
    }
  }

  const generateAudio = async (text) => {
    setStep(2)
    console.log('[STEP 2] Starting audio generation...', { textLength: text.length, useElevenLabs })

    try {
      const response = await axios.post('http://localhost:5000/api/generate/audio', {
        text,
        use_elevenlabs: useElevenLabs
      })

      console.log('[STEP 2] Audio generation response:', response.data)

      if (response.data.success) {
        console.log('[STEP 2] ✅ Audio generated successfully!', {
          audioPath: response.data.audio_path,
          duration: response.data.duration
        })

        // Extract just the filename from the path
        const audioFilename = response.data.audio_path.split(/[\\/]/).pop()
        console.log('[STEP 2] Extracted audio filename:', audioFilename)

        setGeneratedData(prev => ({
          ...prev,
          audio_path: audioFilename,  // Store only filename
          audio_path_full: response.data.audio_path,  // Store full path for reference
          duration: response.data.duration
        }))
        setStep(3)
        await generateSubtitles(text, response.data.duration)
      } else {
        throw new Error('Audio generation returned success: false')
      }
    } catch (error) {
      console.error('[STEP 2] ❌ Audio generation failed:', error)
      const errorMsg = 'Failed to generate audio: ' + (error.response?.data?.error || error.message)
      setError(errorMsg)
      alert('❌ Error: ' + errorMsg)
      setLoading(false)
    }
  }

  const generateSubtitles = async (text, duration) => {
    setStep(3)
    console.log('[STEP 3] Starting subtitle generation...', { textLength: text.length, duration, wordsPerChunk })

    try {
      const response = await axios.post('http://localhost:5000/api/generate/subtitles', {
        text,
        duration,
        words_per_chunk: wordsPerChunk
      })

      console.log('[STEP 3] Subtitle generation response:', response.data)

      if (response.data.success) {
        console.log('[STEP 3] ✅ Subtitles generated successfully!', {
          subtitleCount: response.data.subtitles.length
        })

        setGeneratedData(prev => {
          const newData = { ...prev, subtitles: response.data.subtitles }
          console.log('[STEP 3] About to call generateVideo with audioPath:', newData.audio_path)
          // Call generateVideo with complete data
          generateVideo(text, response.data.subtitles, newData.audio_path)
          return newData
        })
        setStep(4)
      } else {
        throw new Error('Subtitle generation returned success: false')
      }
    } catch (error) {
      console.error('[STEP 3] ❌ Subtitle generation failed:', error)
      const errorMsg = 'Failed to generate subtitles: ' + (error.response?.data?.error || error.message)
      setError(errorMsg)
      alert('❌ Error: ' + errorMsg)
      setLoading(false)
    }
  }

  const generateVideo = async (text, subtitles, audioPath) => {
    setStep(4)
    console.log('[STEP 4] Starting video generation...', {
      textLength: text.length,
      subtitleCount: subtitles.length,
      audioPath,
      selectedGenre,
      selectedBackground
    })

    try {
      const videoPayload = {
        story_text: text,
        genre: selectedGenre,
        audio_path: audioPath,
        subtitles,
        background_video: selectedBackground || null
      }

      console.log('[STEP 4] Sending video generation request:', videoPayload)

      const response = await axios.post('http://localhost:5000/api/generate/video', videoPayload)

      console.log('[STEP 4] Video generation response:', response.data)

      if (response.data.success) {
        console.log('[STEP 4] ✅ Video generated successfully!', {
          videoPath: response.data.video_path
        })

        setGeneratedData(prev => ({
          ...prev,
          video_path: response.data.video_path,
          metadata: response.data.metadata
        }))
        setStep(5)
        setLoading(false)
        alert('✅ Video generated successfully! Check the preview below.')
      } else {
        throw new Error('Video generation returned success: false')
      }
    } catch (error) {
      console.error('[STEP 4] ❌ Video generation failed:', error)
      console.error('[STEP 4] Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })

      const errorMsg = 'Failed to generate video: ' + (error.response?.data?.error || error.message)
      setError(errorMsg)
      alert('❌ Error: ' + errorMsg)
      setLoading(false)
    }
  }

  const handleGenerate = () => {
    if (useCustomStory && !customStory.trim()) {
      setError('Please enter a custom story')
      return
    }
    generateStory()
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Video Generator</h1>
        <p className="text-gray-400">Create viral Shorts in seconds</p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Settings Panel */}
        <div className="col-span-1 space-y-6">
          <div className="card">
            <h3 className="font-bold mb-4">Settings</h3>

            {/* Genre Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Genre</label>
              <select
                value={selectedGenre}
                onChange={(e) => setSelectedGenre(e.target.value)}
                className="input w-full"
                disabled={loading}
              >
                {genres.map(genre => (
                  <option key={genre} value={genre}>{genre}</option>
                ))}
              </select>
            </div>

            {/* Background Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Background</label>
              <select
                value={selectedBackground}
                onChange={(e) => setSelectedBackground(e.target.value)}
                className="input w-full"
                disabled={loading}
              >
                <option value="">Random</option>
                {backgrounds.map(bg => (
                  <option key={bg} value={bg}>{bg}</option>
                ))}
              </select>
            </div>

            {/* Subtitle Settings */}
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
                disabled={loading}
              />
            </div>

            {/* TTS Selection */}
            <div className="mb-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={useElevenLabs}
                  onChange={(e) => setUseElevenLabs(e.target.checked)}
                  disabled={loading}
                />
                <span className="text-sm">Use ElevenLabs TTS (Premium)</span>
              </label>
            </div>

            {/* Custom Story Toggle */}
            <div className="mb-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={useCustomStory}
                  onChange={(e) => setUseCustomStory(e.target.checked)}
                  disabled={loading}
                />
                <span className="text-sm">Use Custom Story</span>
              </label>
            </div>

            {useCustomStory && (
              <div className="mb-4">
                <textarea
                  value={customStory}
                  onChange={(e) => setCustomStory(e.target.value)}
                  placeholder="Enter your custom story..."
                  className="input w-full h-32 resize-none"
                  disabled={loading}
                />
              </div>
            )}

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader size={20} className="animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Play size={20} />
                  Generate Video
                </>
              )}
            </button>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="col-span-2 space-y-6">
          {/* Progress Steps */}
          <div className="card">
            <h3 className="font-bold mb-4">Generation Progress</h3>
            <div className="space-y-3">
              <ProgressStep
                number={1}
                title="Generate Story"
                active={step >= 1}
                completed={step > 1}
                loading={loading && step === 1}
              />
              <ProgressStep
                number={2}
                title="Generate Audio"
                active={step >= 2}
                completed={step > 2}
                loading={loading && step === 2}
              />
              <ProgressStep
                number={3}
                title="Generate Subtitles"
                active={step >= 3}
                completed={step > 3}
                loading={loading && step === 3}
              />
              <ProgressStep
                number={4}
                title="Create Video"
                active={step >= 4}
                completed={step > 4}
                loading={loading && step === 4}
              />
              <ProgressStep
                number={5}
                title="Complete!"
                active={step >= 5}
                completed={step >= 5}
                loading={false}
              />
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="card bg-red-900 bg-opacity-20 border-red-800">
              <div className="flex items-start gap-3">
                <AlertCircle size={20} className="text-red-400 mt-0.5" />
                <div>
                  <p className="font-medium text-red-400">Generation Error</p>
                  <p className="text-sm text-red-300 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Story Preview */}
          {generatedData.story && (
            <div className="card">
              <h3 className="font-bold mb-3">Generated Story</h3>
              <div className="bg-dark-hover p-4 rounded-lg">
                <p className="text-sm whitespace-pre-wrap">{generatedData.story.story}</p>
              </div>
              <div className="flex items-center gap-4 mt-3 text-sm text-gray-400">
                <span>{generatedData.story.word_count} words</span>
                <span>~{generatedData.story.estimated_duration}s</span>
              </div>
            </div>
          )}

          {/* Audio Preview */}
          {generatedData.audio_path && !generatedData.video_path && (
            <div className="card">
              <h3 className="font-bold mb-3 flex items-center gap-2">
                <Music size={20} />
                Audio Preview
              </h3>
              <AudioPlayer
                src={`http://localhost:5000/api/files/audio/${generatedData.audio_path.split('/').pop()}`}
              />
              <p className="text-sm text-gray-400 mt-2">
                Duration: {generatedData.duration?.toFixed(1)}s
              </p>
            </div>
          )}

          {/* Video Result */}
          {generatedData.video_path && (
            <div className="card bg-green-900 bg-opacity-20 border-green-800">
              <div className="flex items-start gap-3 mb-4">
                <CheckCircle size={24} className="text-green-400" />
                <div>
                  <h3 className="font-bold text-green-400">Video Generated!</h3>
                  <p className="text-sm text-green-300 mt-1">Your video is ready for review</p>
                </div>
              </div>

              {/* Video Preview */}
              <div className="mb-4">
                <VideoPlayer
                  src={`http://localhost:5000/api/files/video/${generatedData.video_path.split('/').pop().split('\\').pop()}`}
                  className="rounded-lg"
                />
              </div>

              {/* Metadata Display */}
              {generatedData.metadata && (
                <div className="mb-4 p-4 bg-dark-hover rounded-lg">
                  <h4 className="font-bold mb-2 text-sm">Publishing Info</h4>
                  <div className="space-y-2 text-sm">
                    {generatedData.metadata.publishing?.caption && (
                      <div>
                        <p className="text-gray-400">Caption:</p>
                        <p className="text-white">{generatedData.metadata.publishing.caption}</p>
                      </div>
                    )}
                    {generatedData.metadata.publishing?.hashtags_string && (
                      <div>
                        <p className="text-gray-400">Hashtags:</p>
                        <p className="text-primary-400">{generatedData.metadata.publishing.hashtags_string}</p>
                      </div>
                    )}
                    {generatedData.metadata.optimization?.viral_score && (
                      <div>
                        <p className="text-gray-400">Viral Score:</p>
                        <p className="text-green-400 font-bold">
                          {generatedData.metadata.optimization.viral_score}/100
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="flex flex-wrap gap-2">
                <a
                  href={`http://localhost:5000/api/files/video/${generatedData.video_path.split('/').pop().split('\\').pop()}`}
                  download
                  className="btn-primary flex items-center gap-2"
                >
                  <Download size={20} />
                  Download Video
                </a>
                <button
                  onClick={() => {
                    const path = generatedData.video_path.replace(/\//g, '\\')
                    navigator.clipboard.writeText(path)
                    alert('Path copied to clipboard!')
                  }}
                  className="btn-secondary flex items-center gap-2"
                >
                  <FolderOpen size={20} />
                  Copy Path
                </button>
                <button
                  onClick={() => {
                    setGeneratedData({})
                    setStep(1)
                    setError('')
                  }}
                  className="btn-secondary"
                >
                  Generate Another
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function ProgressStep({ number, title, active, completed, loading }) {
  return (
    <div className={`flex items-center gap-3 ${!active && 'opacity-40'}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
          completed
            ? 'bg-green-600 text-white'
            : active
            ? 'bg-primary-600 text-white'
            : 'bg-dark-hover text-gray-500'
        }`}
      >
        {loading ? (
          <Loader size={16} className="animate-spin" />
        ) : completed ? (
          <CheckCircle size={16} />
        ) : (
          number
        )}
      </div>
      <span className={`font-medium ${completed && 'text-green-400'}`}>{title}</span>
    </div>
  )
}
