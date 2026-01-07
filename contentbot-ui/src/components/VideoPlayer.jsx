import { useState } from 'react'
import { Play, Pause, Volume2, VolumeX, Maximize } from 'lucide-react'

export default function VideoPlayer({ src, poster, className = '' }) {
  const [playing, setPlaying] = useState(false)
  const [muted, setMuted] = useState(false)

  const handlePlayPause = (e) => {
    const video = e.target.closest('.video-container').querySelector('video')
    if (video.paused) {
      video.play()
      setPlaying(true)
    } else {
      video.pause()
      setPlaying(false)
    }
  }

  const handleMute = (e) => {
    const video = e.target.closest('.video-container').querySelector('video')
    video.muted = !video.muted
    setMuted(video.muted)
  }

  const handleFullscreen = (e) => {
    const video = e.target.closest('.video-container').querySelector('video')
    if (video.requestFullscreen) {
      video.requestFullscreen()
    }
  }

  return (
    <div className={`video-container relative group ${className}`}>
      <video
        className="w-full h-full rounded-lg bg-dark-bg"
        poster={poster}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        controls
        preload="metadata"
      >
        <source src={src} type="video/mp4; codecs=avc1.42E01E,mp4a.40.2" />
        <p>Your browser doesn't support HTML5 video. <a href={src}>Download the video</a> instead.</p>
      </video>

      {/* Custom Controls Overlay (optional) */}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
        <div className="flex items-center gap-3 pointer-events-auto">
          <button
            onClick={handlePlayPause}
            className="p-2 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
          >
            {playing ? <Pause size={20} /> : <Play size={20} />}
          </button>

          <button
            onClick={handleMute}
            className="p-2 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
          >
            {muted ? <VolumeX size={20} /> : <Volume2 size={20} />}
          </button>

          <div className="flex-1"></div>

          <button
            onClick={handleFullscreen}
            className="p-2 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
          >
            <Maximize size={20} />
          </button>
        </div>
      </div>
    </div>
  )
}
