import { useState, useEffect } from 'react'
import { Play, TrendingUp, Clock, CheckCircle, Eye, X } from 'lucide-react'
import axios from 'axios'
import VideoPlayer from '../components/VideoPlayer'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalVideos: 0,
    todayVideos: 0,
    totalViews: 0,
    avgDuration: 0
  })
  const [recentVideos, setRecentVideos] = useState([])
  const [previewVideo, setPreviewVideo] = useState(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/files/videos')
      if (response.data.success) {
        setRecentVideos(response.data.videos.slice(0, 5))
        setStats({
          totalVideos: response.data.videos.length,
          todayVideos: response.data.videos.filter(v =>
            new Date(v.modified * 1000).toDateString() === new Date().toDateString()
          ).length,
          totalViews: 0, // TODO: Add analytics
          avgDuration: 60
        })
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-400">Overview of your content creation</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<Play size={24} />}
          label="Total Videos"
          value={stats.totalVideos}
          trend="+12%"
        />
        <StatCard
          icon={<TrendingUp size={24} />}
          label="Today"
          value={stats.todayVideos}
          trend="New"
        />
        <StatCard
          icon={<Clock size={24} />}
          label="Avg Duration"
          value={`${stats.avgDuration}s`}
          trend="Optimal"
        />
        <StatCard
          icon={<CheckCircle size={24} />}
          label="Success Rate"
          value="98%"
          trend="+5%"
        />
      </div>

      {/* Recent Videos */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Recent Videos</h2>
        {recentVideos.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <Play size={48} className="mx-auto mb-4 opacity-50" />
            <p>No videos generated yet</p>
            <p className="text-sm mt-2">Go to Generator to create your first video</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recentVideos.map((video, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-dark-hover rounded-lg hover:bg-opacity-80 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center">
                    <Play size={20} />
                  </div>
                  <div>
                    <p className="font-medium">{video.name}</p>
                    <p className="text-sm text-gray-400">
                      {new Date(video.modified * 1000).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-400">
                    {(video.size / (1024 * 1024)).toFixed(2)} MB
                  </span>
                  <button
                    onClick={() => setPreviewVideo(video)}
                    className="btn-secondary px-3 py-1 text-sm flex items-center gap-2"
                  >
                    <Eye size={16} />
                    Preview
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Video Preview Modal */}
      {previewVideo && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8">
          <div className="bg-dark-card rounded-lg max-w-2xl w-full max-h-[90vh] overflow-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">{previewVideo.name}</h3>
                <button
                  onClick={() => setPreviewVideo(null)}
                  className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
                >
                  <X size={20} />
                </button>
              </div>

              <VideoPlayer
                src={`http://localhost:5000/api/files/video/${previewVideo.name}`}
                className="mb-4"
              />

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-400">Size</p>
                  <p className="font-medium">{(previewVideo.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
                <div>
                  <p className="text-gray-400">Created</p>
                  <p className="font-medium">
                    {new Date(previewVideo.modified * 1000).toLocaleString()}
                  </p>
                </div>
              </div>

              {previewVideo.metadata && (
                <div className="mt-4 p-4 bg-dark-hover rounded-lg">
                  <p className="text-sm text-gray-400 mb-2">Metadata</p>
                  <pre className="text-xs overflow-auto">
                    {JSON.stringify(previewVideo.metadata, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function StatCard({ icon, label, value, trend }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 bg-primary-600 bg-opacity-20 rounded-lg text-primary-400">
          {icon}
        </div>
        <span className="text-sm text-green-400">{trend}</span>
      </div>
      <p className="text-2xl font-bold mb-1">{value}</p>
      <p className="text-sm text-gray-400">{label}</p>
    </div>
  )
}
