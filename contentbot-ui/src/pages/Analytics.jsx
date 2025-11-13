import { useState, useEffect } from 'react'
import { TrendingUp, Eye, Clock, ThumbsUp } from 'lucide-react'
import axios from 'axios'

export default function Analytics() {
  const [videos, setVideos] = useState([])
  const [stats, setStats] = useState({
    totalVideos: 0,
    totalDuration: 0,
    avgSize: 0,
    thisWeek: 0
  })

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/files/videos')
      if (response.data.success) {
        const vids = response.data.videos
        setVideos(vids)

        const totalSize = vids.reduce((sum, v) => sum + v.size, 0)
        const avgSize = vids.length > 0 ? totalSize / vids.length : 0

        const weekAgo = Date.now() / 1000 - (7 * 24 * 60 * 60)
        const thisWeek = vids.filter(v => v.modified > weekAgo).length

        setStats({
          totalVideos: vids.length,
          totalDuration: vids.length * 60, // Estimate
          avgSize: avgSize / (1024 * 1024),
          thisWeek
        })
      }
    } catch (error) {
      console.error('Failed to load analytics:', error)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Analytics</h1>
        <p className="text-gray-400">Track your content performance</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<TrendingUp size={24} />}
          label="Total Videos"
          value={stats.totalVideos}
          color="blue"
        />
        <StatCard
          icon={<Clock size={24} />}
          label="This Week"
          value={stats.thisWeek}
          color="green"
        />
        <StatCard
          icon={<Eye size={24} />}
          label="Avg Size"
          value={`${stats.avgSize.toFixed(1)}MB`}
          color="purple"
        />
        <StatCard
          icon={<ThumbsUp size={24} />}
          label="Success Rate"
          value="100%"
          color="teal"
        />
      </div>

      {/* Production Timeline */}
      <div className="card mb-6">
        <h3 className="font-bold mb-4">Production Timeline</h3>
        <div className="h-64 flex items-end justify-between gap-2">
          {[12, 8, 15, 23, 19, 28, 35].map((value, index) => (
            <div key={index} className="flex-1 flex flex-col items-center">
              <div
                className="w-full bg-primary-600 rounded-t-lg transition-all hover:bg-primary-500"
                style={{ height: `${(value / 35) * 100}%` }}
              ></div>
              <p className="text-xs text-gray-400 mt-2">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index]}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Genre Breakdown */}
      <div className="grid grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-bold mb-4">Genre Distribution</h3>
          <div className="space-y-3">
            {[
              { genre: 'Comedy', count: 45, percentage: 35 },
              { genre: 'AITA', count: 38, percentage: 30 },
              { genre: 'Terror', count: 25, percentage: 20 },
              { genre: 'Relationship', count: 19, percentage: 15 }
            ].map((item) => (
              <div key={item.genre}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm">{item.genre}</span>
                  <span className="text-sm text-gray-400">{item.count} videos</span>
                </div>
                <div className="h-2 bg-dark-hover rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary-600 rounded-full"
                    style={{ width: `${item.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="font-bold mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {videos.slice(0, 5).map((video, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-dark-hover rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <div>
                    <p className="text-sm font-medium">{video.name}</p>
                    <p className="text-xs text-gray-400">
                      {new Date(video.modified * 1000).toLocaleString()}
                    </p>
                  </div>
                </div>
                <span className="text-xs text-gray-400">
                  {(video.size / (1024 * 1024)).toFixed(1)}MB
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, color }) {
  const colorClasses = {
    blue: 'bg-blue-600 bg-opacity-20 text-blue-400',
    green: 'bg-green-600 bg-opacity-20 text-green-400',
    purple: 'bg-purple-600 bg-opacity-20 text-purple-400',
    teal: 'bg-teal-600 bg-opacity-20 text-teal-400'
  }

  return (
    <div className="card">
      <div className={`p-2 rounded-lg ${colorClasses[color]} w-fit mb-4`}>
        {icon}
      </div>
      <p className="text-2xl font-bold mb-1">{value}</p>
      <p className="text-sm text-gray-400">{label}</p>
    </div>
  )
}
