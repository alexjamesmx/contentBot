import { useState, useRef, useEffect } from 'react'
import { Play, Pause, Volume2, VolumeX, Loader } from 'lucide-react'

export default function AudioPlayer({ src, className = '' }) {
  const [playing, setPlaying] = useState(false)
  const [muted, setMuted] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const audioRef = useRef(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio || !src) return

    setLoading(true)
    setError(null)
    setPlaying(false)

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => {
      setDuration(audio.duration)
      setLoading(false)
    }
    const handleError = (e) => {
      console.error('Audio error:', e)
      setError('Failed to load audio')
      setLoading(false)
    }
    const handleCanPlay = () => setLoading(false)

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('canplay', handleCanPlay)
    audio.addEventListener('error', handleError)

    // Force reload when src changes
    audio.load()

    return () => {
      audio.pause()
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('canplay', handleCanPlay)
      audio.removeEventListener('error', handleError)
    }
  }, [src])

  const handlePlayPause = async () => {
    if (!audioRef.current || loading || error) return

    try {
      if (audioRef.current.paused) {
        await audioRef.current.play()
        setPlaying(true)
      } else {
        audioRef.current.pause()
        setPlaying(false)
      }
    } catch (err) {
      console.error('Play error:', err)
      setError('Failed to play audio')
    }
  }

  const handleMute = () => {
    audioRef.current.muted = !audioRef.current.muted
    setMuted(audioRef.current.muted)
  }

  const handleSeek = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const percent = (e.clientX - rect.left) / rect.width
    audioRef.current.currentTime = percent * duration
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (error) {
    return (
      <div className={`flex items-center gap-3 p-4 bg-dark-card rounded-lg border border-red-500 ${className}`}>
        <p className="text-sm text-red-400">{error}</p>
      </div>
    )
  }

  return (
    <div className={`flex items-center gap-3 p-4 bg-dark-card rounded-lg border border-dark-border ${className}`}>
      <audio
        ref={audioRef}
        src={src}
        onEnded={() => setPlaying(false)}
        crossOrigin="anonymous"
        preload="auto"
      />

      <button
        onClick={handlePlayPause}
        disabled={loading}
        className="p-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-full transition-colors"
      >
        {loading ? <Loader size={16} className="animate-spin" /> : playing ? <Pause size={16} /> : <Play size={16} />}
      </button>

      <div className="flex-1 flex items-center gap-3">
        <span className="text-xs text-gray-400">{formatTime(currentTime)}</span>

        <div
          className="flex-1 h-2 bg-dark-hover rounded-full cursor-pointer relative"
          onClick={handleSeek}
        >
          <div
            className="h-full bg-primary-600 rounded-full transition-all"
            style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
          ></div>
        </div>

        <span className="text-xs text-gray-400">{formatTime(duration)}</span>
      </div>

      <button
        onClick={handleMute}
        disabled={loading}
        className="p-2 bg-dark-hover hover:bg-opacity-80 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-full transition-colors"
      >
        {muted ? <VolumeX size={16} /> : <Volume2 size={16} />}
      </button>
    </div>
  )
}
