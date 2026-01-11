import { useState, useEffect } from 'react'
import { Play, TrendingUp, Clock, CheckCircle, Eye, X, Zap, Download, Calendar, Target, DollarSign, AlertCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import VideoPlayer from '../components/VideoPlayer'

export default function Dashboard() {
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    totalVideos: 0,
    todayVideos: 0,
    weekVideos: 0,
    monthVideos: 0,
    avgDuration: 0,
    totalDuration: 0,
    monetizable: 0,
    monetizablePercentage: 0,
    genreBreakdown: {}
  })
  const [recentVideos, setRecentVideos] = useState([])
  const [previewVideo, setPreviewVideo] = useState(null)
  const [weeklyGoal, setWeeklyGoal] = useState(60)
  const [dailyTarget, setDailyTarget] = useState(10)

  useEffect(() => {
    loadDashboardData()
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/analytics/detailed')
      if (response.data.success) {
        const { stats: analyticsStats, recentVideos: vids, genreBreakdown } = response.data

        const now = Date.now() / 1000
        const today = new Date().setHours(0, 0, 0, 0) / 1000
        const weekAgo = now - (7 * 24 * 60 * 60)
        const monthAgo = now - (30 * 24 * 60 * 60)

        setRecentVideos(vids.slice(0, 5))
        setStats({
          totalVideos: analyticsStats.totalVideos,
          todayVideos: vids.filter(v => v.modified >= today).length,
          weekVideos: analyticsStats.thisWeek,
          monthVideos: vids.filter(v => v.modified >= monthAgo).length,
          avgDuration: analyticsStats.avgDuration,
          totalDuration: analyticsStats.totalDuration,
          monetizable: analyticsStats.monetizable,
          monetizablePercentage: analyticsStats.monetizablePercentage,
          genreBreakdown: genreBreakdown || {}
        })
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    }
  }

  const handleQuickAction = async (action) => {
    if (action === 'generate_comedy') {
      navigate('/generator')
    } else if (action === 'export_today') {
      const todayVids = recentVideos.filter(v =>
        new Date(v.modified * 1000).toDateString() === new Date().toDateString()
      )
      if (todayVids.length === 0) {
        alert('No videos generated today')
        return
      }
      const dataStr = JSON.stringify(todayVids, null, 2)
      const blob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `videos_today_${Date.now()}.json`
      link.click()
    } else if (action === 'view_latest') {
      if (recentVideos.length > 0) {
        setPreviewVideo(recentVideos[0])
      }
    }
  }

  const goalProgress = (stats.weekVideos / weeklyGoal) * 100
  const dailyProgress = (stats.todayVideos / dailyTarget) * 100
  const daysThisWeek = new Date().getDay() || 7
  const expectedWeekProgress = (daysThisWeek / 7) * weeklyGoal

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Production Command Center</h1>
        <p className="text-gray-400">Real-time overview of your content factory</p>
      </div>

      {/* Today's Goals */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="card bg-gradient-to-br from-primary-900/20 to-blue-900/20 border-primary-800">
          <div className="flex items-center gap-3 mb-4">
            <Target size={24} className="text-primary-400" />
            <div>
              <h3 className="font-bold">Daily Target</h3>
              <p className="text-xs text-gray-400">{stats.todayVideos} / {dailyTarget} videos</p>
            </div>
          </div>
          <div className="h-3 bg-dark-hover rounded-full overflow-hidden mb-2">
            <div
              className={`h-full rounded-full transition-all ${
                dailyProgress >= 100 ? 'bg-green-500' : dailyProgress >= 50 ? 'bg-primary-500' : 'bg-yellow-500'
              }`}
              style={{ width: `${Math.min(dailyProgress, 100)}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-400">
            {dailyProgress >= 100 ? '✓ Daily goal achieved!' : dailyProgress >= 50 ? 'On track' : 'Need to speed up'}
          </p>
        </div>

        <div className="card bg-gradient-to-br from-green-900/20 to-emerald-900/20 border-green-800">
          <div className="flex items-center gap-3 mb-4">
            <Calendar size={24} className="text-green-400" />
            <div>
              <h3 className="font-bold">Weekly Goal</h3>
              <p className="text-xs text-gray-400">{stats.weekVideos} / {weeklyGoal} videos</p>
            </div>
          </div>
          <div className="h-3 bg-dark-hover rounded-full overflow-hidden mb-2">
            <div
              className="h-full bg-green-500 rounded-full transition-all"
              style={{ width: `${Math.min(goalProgress, 100)}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-400">
            {stats.weekVideos >= expectedWeekProgress
              ? `✓ Ahead of schedule (+${Math.round(stats.weekVideos - expectedWeekProgress)} videos)`
              : `Behind by ${Math.round(expectedWeekProgress - stats.weekVideos)} videos`}
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <StatCard
          icon={<Play size={24} />}
          label="Total Videos"
          value={stats.totalVideos}
          subtitle={`${stats.monthVideos} this month`}
          color="blue"
        />
        <StatCard
          icon={<Clock size={24} />}
          label="Avg Duration"
          value={`${stats.avgDuration.toFixed(0)}s`}
          subtitle={stats.avgDuration >= 60 && stats.avgDuration <= 90 ? '✓ Monetizable' : '⚠️ Adjust range'}
          color={stats.avgDuration >= 60 && stats.avgDuration <= 90 ? 'green' : 'yellow'}
        />
        <StatCard
          icon={<CheckCircle size={24} />}
          label="Monetizable"
          value={`${stats.monetizablePercentage.toFixed(0)}%`}
          subtitle={`${stats.monetizable}/${stats.totalVideos} videos 60s+`}
          color={stats.monetizablePercentage >= 80 ? 'green' : 'yellow'}
        />
      </div>

      {/* Quick Actions */}
      <div className="card mb-8">
        <h3 className="font-bold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-4 gap-3">
          <button
            onClick={() => handleQuickAction('generate_comedy')}
            className="p-4 bg-primary-900 bg-opacity-20 border border-primary-800 rounded-lg hover:bg-opacity-30 transition-all text-left"
          >
            <Zap size={20} className="text-primary-400 mb-2" />
            <p className="font-medium text-sm">Generate Video</p>
            <p className="text-xs text-gray-400">Quick single video</p>
          </button>
          <button
            onClick={() => navigate('/generator')}
            className="p-4 bg-green-900 bg-opacity-20 border border-green-800 rounded-lg hover:bg-opacity-30 transition-all text-left"
          >
            <Play size={20} className="text-green-400 mb-2" />
            <p className="font-medium text-sm">Batch Mode</p>
            <p className="text-xs text-gray-400">Generate 5-20 videos</p>
          </button>
          <button
            onClick={() => handleQuickAction('export_today')}
            className="p-4 bg-blue-900 bg-opacity-20 border border-blue-800 rounded-lg hover:bg-opacity-30 transition-all text-left"
          >
            <Download size={20} className="text-blue-400 mb-2" />
            <p className="font-medium text-sm">Export Today</p>
            <p className="text-xs text-gray-400">Download as JSON</p>
          </button>
          <button
            onClick={() => handleQuickAction('view_latest')}
            className="p-4 bg-purple-900 bg-opacity-20 border border-purple-800 rounded-lg hover:bg-opacity-30 transition-all text-left"
          >
            <Eye size={20} className="text-purple-400 mb-2" />
            <p className="font-medium text-sm">View Latest</p>
            <p className="text-xs text-gray-400">Open in player</p>
          </button>
        </div>
      </div>

      {/* Genre Performance & Recent Videos Grid */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="card">
          <h3 className="font-bold mb-4">Genre Distribution</h3>
          <div className="space-y-3">
            {Object.keys(stats.genreBreakdown).length > 0 ? (
              Object.entries(stats.genreBreakdown)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([genre, count]) => {
                  const percentage = (count / stats.totalVideos * 100).toFixed(0)
                  return (
                    <div key={genre}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm capitalize">{genre.replace('_', ' ')}</span>
                        <span className="text-xs text-gray-400">{count} ({percentage}%)</span>
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
              <p className="text-sm text-gray-400 text-center py-8">No data yet</p>
            )}
          </div>
        </div>

        <div className="col-span-2 card">
          <h3 className="font-bold mb-4">Production Insights</h3>
          <div className="space-y-3">
            {stats.avgDuration >= 60 && stats.avgDuration <= 90 ? (
              <div className="flex items-start gap-3 p-3 bg-green-900 bg-opacity-20 rounded-lg border border-green-800">
                <CheckCircle size={20} className="text-green-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-green-400">Optimal Duration</p>
                  <p className="text-xs text-green-300 mt-1">
                    Your videos average {stats.avgDuration.toFixed(0)}s - perfect for TikTok Creator Rewards
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex items-start gap-3 p-3 bg-yellow-900 bg-opacity-20 rounded-lg border border-yellow-800">
                <AlertCircle size={20} className="text-yellow-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-yellow-400">Duration Warning</p>
                  <p className="text-xs text-yellow-300 mt-1">
                    Avg {stats.avgDuration.toFixed(0)}s - Target 60-90s for monetization
                  </p>
                </div>
              </div>
            )}

            {stats.weekVideos >= weeklyGoal ? (
              <div className="flex items-start gap-3 p-3 bg-green-900 bg-opacity-20 rounded-lg border border-green-800">
                <TrendingUp size={20} className="text-green-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-green-400">Weekly Goal Achieved!</p>
                  <p className="text-xs text-green-300 mt-1">
                    {stats.weekVideos} videos this week - you are crushing it!
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex items-start gap-3 p-3 bg-primary-900 bg-opacity-20 rounded-lg border border-primary-800">
                <Target size={20} className="text-primary-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-primary-400">Keep Going</p>
                  <p className="text-xs text-primary-300 mt-1">
                    {weeklyGoal - stats.weekVideos} more videos needed to hit weekly goal
                  </p>
                </div>
              </div>
            )}

            {Object.keys(stats.genreBreakdown).length > 0 && (
              <div className="flex items-start gap-3 p-3 bg-blue-900 bg-opacity-20 rounded-lg border border-blue-800">
                <Eye size={20} className="text-blue-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-blue-400">Top Genre</p>
                  <p className="text-xs text-blue-300 mt-1">
                    Most productive: {Object.entries(stats.genreBreakdown).sort((a, b) => b[1] - a[1])[0]?.[0]?.replace('_', ' ') || 'N/A'}
                    ({Object.entries(stats.genreBreakdown).sort((a, b) => b[1] - a[1])[0]?.[1] || 0} videos)
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
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
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                    index === 0 ? 'bg-green-600' : 'bg-primary-600'
                  }`}>
                    <Play size={20} />
                  </div>
                  <div>
                    <p className="font-medium">{video.name}</p>
                    <p className="text-sm text-gray-400 capitalize">
                      {video.genre?.replace('_', ' ')} •
                      {video.duration ? ` ${video.duration.toFixed(0)}s` : ''} •
                      {new Date(video.modified * 1000).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {video.duration >= 60 && (
                    <span className="text-xs px-2 py-1 rounded bg-green-900 bg-opacity-30 text-green-400 border border-green-800">
                      Monetizable
                    </span>
                  )}
                  <span className="text-sm text-gray-400">
                    {(video.size / (1024 * 1024)).toFixed(1)} MB
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

              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-gray-400">Size</p>
                  <p className="font-medium">{(previewVideo.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
                <div>
                  <p className="text-gray-400">Duration</p>
                  <p className="font-medium">{previewVideo.duration ? `${previewVideo.duration.toFixed(0)}s` : 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-400">Created</p>
                  <p className="font-medium">
                    {new Date(previewVideo.modified * 1000).toLocaleDateString()}
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

function StatCard({ icon, label, value, subtitle, color = 'blue' }) {
  const colorClasses = {
    blue: 'bg-blue-600 bg-opacity-20 text-blue-400',
    green: 'bg-green-600 bg-opacity-20 text-green-400',
    purple: 'bg-purple-600 bg-opacity-20 text-purple-400',
    yellow: 'bg-yellow-600 bg-opacity-20 text-yellow-400',
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
