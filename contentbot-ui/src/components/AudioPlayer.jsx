import { useState, useRef, useEffect } from 'react'
import { Play, Pause, Volume2, VolumeX } from 'lucide-react'

export default function AudioPlayer({ src, className = '' }) {
  const [playing, setPlaying] = useState(false)
  const [muted, setMuted] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const audioRef = useRef(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration)

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
    }
  }, [])

  const handlePlayPause = () => {
    if (audioRef.current.paused) {
      audioRef.current.play()
      setPlaying(true)
    } else {
      audioRef.current.pause()
      setPlaying(false)
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

  return (
    <div className={`flex items-center gap-3 p-4 bg-dark-card rounded-lg border border-dark-border ${className}`}>
      <audio ref={audioRef} src={src} onEnded={() => setPlaying(false)} />

      <button
        onClick={handlePlayPause}
        className="p-2 bg-primary-600 hover:bg-primary-700 rounded-full transition-colors"
      >
        {playing ? <Pause size={16} /> : <Play size={16} />}
      </button>

      <div className="flex-1 flex items-center gap-3">
        <span className="text-xs text-gray-400">{formatTime(currentTime)}</span>

        <div
          className="flex-1 h-2 bg-dark-hover rounded-full cursor-pointer relative"
          onClick={handleSeek}
        >
          <div
            className="h-full bg-primary-600 rounded-full"
            style={{ width: `${(currentTime / duration) * 100}%` }}
          ></div>
        </div>

        <span className="text-xs text-gray-400">{formatTime(duration)}</span>
      </div>

      <button
        onClick={handleMute}
        className="p-2 bg-dark-hover hover:bg-opacity-80 rounded-full transition-colors"
      >
        {muted ? <VolumeX size={16} /> : <Volume2 size={16} />}
      </button>
    </div>
  )
}
