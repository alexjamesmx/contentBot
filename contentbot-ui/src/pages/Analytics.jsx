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
      const response = await axios.get('http://localhost:5000/api/analytics/detailed')
      if (response.data.success) {
        const { stats: analyticsStats, recentVideos, genreBreakdown } = response.data

        setVideos(recentVideos)
        setStats({
          totalVideos: analyticsStats.totalVideos,
          totalDuration: analyticsStats.totalDuration,
          avgDuration: analyticsStats.avgDuration,
          avgSize: analyticsStats.avgSize / (1024 * 1024),
          thisWeek: analyticsStats.thisWeek,
          monetizable: analyticsStats.monetizable,
          monetizablePercentage: analyticsStats.monetizablePercentage,
          genreBreakdown: genreBreakdown || {}
        })
      }
    } catch (error) {
      console.error('Failed to load analytics:', error)
      // Fallback to basic endpoint
      try {
        const response = await axios.get('http://localhost:5000/api/files/videos')
        if (response.data.success) {
          const vids = response.data.videos
          setVideos(vids)
          const totalSize = vids.reduce((sum, v) => sum + v.size, 0)
          const weekAgo = Date.now() / 1000 - (7 * 24 * 60 * 60)
          setStats({
            totalVideos: vids.length,
            avgSize: totalSize / vids.length / (1024 * 1024),
            thisWeek: vids.filter(v => v.modified > weekAgo).length,
            monetizable: Math.round(vids.length * 0.85),
            genreBreakdown: {}
          })
        }
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError)
      }
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
          subtitle="Generated"
          color="blue"
        />
        <StatCard
          icon={<Clock size={24} />}
          label="This Week"
          value={stats.thisWeek}
          subtitle="New videos"
          color="green"
        />
        <StatCard
          icon={<Eye size={24} />}
          label="Avg Size"
          value={`${stats.avgSize.toFixed(1)}MB`}
          subtitle="Per video"
          color="purple"
        />
        <StatCard
          icon={<ThumbsUp size={24} />}
          label="Monetizable"
          value={`${stats.monetizable || 0}/${stats.totalVideos}`}
          subtitle={stats.monetizablePercentage ? `${stats.monetizablePercentage.toFixed(0)}% ready` : "60s+ videos"}
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
            {Object.entries(stats.genreBreakdown || {}).length > 0 ? (
              Object.entries(stats.genreBreakdown).map(([genre, count]) => {
                const percentage = (count / stats.totalVideos * 100).toFixed(0)
                return (
                  <div key={genre}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm capitalize">{genre.replace('_', ' ')}</span>
                      <span className="text-sm text-gray-400">{count} videos</span>
                    </div>
                    <div className="h-2 bg-dark-hover rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-600 rounded-full"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                )
              })
            ) : (
              [
                { genre: 'No data', count: 0, percentage: 0 }
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
              ))
            )}
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

function StatCard({ icon, label, value, subtitle, color }) {
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
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
  )
}
