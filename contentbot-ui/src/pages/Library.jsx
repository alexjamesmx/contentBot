import { useState, useEffect } from 'react'
import { Play, Download, Trash2, Loader, RefreshCw } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import AudioPlayer from '../components/AudioPlayer'
import VideoPlayer from '../components/VideoPlayer'

const API_URL = 'http://localhost:5000/api'

export default function Library({ onReuseStory, onReuseAudio }) {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('stories')
  const [loading, setLoading] = useState(false)

  const [stories, setStories] = useState([])
  const [audios, setAudios] = useState([])
  const [videos, setVideos] = useState([])

  useEffect(() => {
    loadContent()
  }, [activeTab])

  const loadContent = async () => {
    setLoading(true)
    try {
      if (activeTab === 'stories') {
        const { data } = await axios.get(`${API_URL}/stories`)
        setStories(data.stories || [])
      } else if (activeTab === 'audios') {
        const { data } = await axios.get(`${API_URL}/files/audios`)
        setAudios(data.audios || [])
      } else if (activeTab === 'videos') {
        const { data } = await axios.get(`${API_URL}/files/videos`)
        setVideos(data.videos || [])
      }
    } catch (error) {
      console.error('Failed to load content:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatSize = (bytes) => {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Content Library</h1>
        <p className="text-gray-400">Reuse your generated content to save tokens and API credits</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-dark-border">
        <button
          onClick={() => setActiveTab('stories')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'stories'
              ? 'text-primary-500 border-b-2 border-primary-500'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Stories ({stories.length})
        </button>
        <button
          onClick={() => setActiveTab('audios')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'audios'
              ? 'text-primary-500 border-b-2 border-primary-500'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Audio ({audios.length})
        </button>
        <button
          onClick={() => setActiveTab('videos')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'videos'
              ? 'text-primary-500 border-b-2 border-primary-500'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Videos ({videos.length})
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="animate-spin" size={32} />
        </div>
      ) : (
        <>
          {/* Stories Tab */}
          {activeTab === 'stories' && (
            <div className="grid gap-4">
              {stories.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  No stories yet. Generate your first story to see it here!
                </div>
              ) : (
                stories.map((story) => (
                  <div key={story.id} className="card">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-bold text-lg">{story.title || 'Untitled Story'}</h3>
                        <p className="text-sm text-gray-400">
                          {story.genre} • {story.word_count} words • {formatDate(story.created_at)}
                        </p>
                      </div>
                      <button
                        onClick={() => {
                          onReuseStory && onReuseStory(story)
                          navigate('/generator')
                        }}
                        className="btn-primary flex items-center gap-2"
                      >
                        <RefreshCw size={16} />
                        Use This Story
                      </button>
                    </div>
                    <p className="text-gray-300 line-clamp-3">{story.story}</p>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Audios Tab */}
          {activeTab === 'audios' && (
            <div className="grid gap-4">
              {audios.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  No audio files yet. Generate audio to see it here!
                </div>
              ) : (
                audios.map((audio) => (
                  <div key={audio.name} className="card">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-bold">{audio.name}</h3>
                        <p className="text-sm text-gray-400">
                          {audio.duration?.toFixed(1)}s • {formatSize(audio.size)} • {formatDate(audio.modified)}
                        </p>
                      </div>
                      <button
                        onClick={() => {
                          onReuseAudio && onReuseAudio(audio)
                          navigate('/generator')
                        }}
                        className="btn-primary flex items-center gap-2"
                      >
                        <RefreshCw size={16} />
                        Use This Audio
                      </button>
                    </div>
                    <AudioPlayer
                      src={`${API_URL}/files/audio/${audio.name}`}
                    />
                  </div>
                ))
              )}
            </div>
          )}

          {/* Videos Tab */}
          {activeTab === 'videos' && (
            <div className="grid gap-4">
              {videos.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  No videos yet. Create your first video to see it here!
                </div>
              ) : (
                videos.map((video) => (
                  <div key={video.name} className="card">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-bold">{video.name}</h3>
                        <p className="text-sm text-gray-400">
                          {formatSize(video.size)} • {formatDate(video.modified)}
                        </p>
                        {video.metadata && (
                          <p className="text-xs text-gray-500 mt-1">
                            Genre: {video.metadata.genre} • Background: {video.metadata.background}
                          </p>
                        )}
                      </div>
                      <a
                        href={`${API_URL}/files/video/${video.name}`}
                        download
                        className="btn-secondary flex items-center gap-2"
                      >
                        <Download size={16} />
                        Download
                      </a>
                    </div>
                    <VideoPlayer
                      src={`${API_URL}/files/video/${video.name}`}
                    />
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
