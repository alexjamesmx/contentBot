import { useState, useEffect } from 'react'
import { Play, Download, Trash2, Loader, RefreshCw, Search, Eye, ChevronRight, X, Music, Video as VideoIcon, FileText, CheckSquare } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import AudioPlayer from '../components/AudioPlayer'
import VideoPlayer from '../components/VideoPlayer'

const API_URL = 'http://localhost:5000/api'

export default function Library({ onReuseStory }) {
  const navigate = useNavigate()

  const [series, setSeries] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [contentFilter, setContentFilter] = useState('all')
  const [assetFilter, setAssetFilter] = useState('all')
  const [selectedGenres, setSelectedGenres] = useState([])
  const [sortBy, setSortBy] = useState('date')
  const [expandedSeries, setExpandedSeries] = useState(null)
  const [bulkMode, setBulkMode] = useState(false)
  const [selectedItems, setSelectedItems] = useState([])

  const genres = ['comedy', 'terror', 'aita', 'genz_chaos', 'relationship_drama']

  useEffect(() => {
    loadAllContent()
  }, [])

  const loadAllContent = async () => {
    setLoading(true)
    try {
      const { data } = await axios.get(`${API_URL}/series`)
      setSeries(data.series || [])
    } catch (error) {
      console.error('Failed to load series:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (isoString) => {
    if (!isoString) return 'Unknown'
    try {
      return new Date(isoString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return 'Unknown'
    }
  }

  const getFilteredSeries = () => {
    let filtered = [...series]

    // Content filter
    if (contentFilter === 'singles') {
      filtered = filtered.filter(s => s.total_parts === 1)
    } else if (contentFilter === 'multi-part') {
      filtered = filtered.filter(s => s.total_parts > 1)
    }

    // Asset filter
    if (assetFilter === 'with-audio') {
      filtered = filtered.filter(s => s.has_audio)
    } else if (assetFilter === 'with-video') {
      filtered = filtered.filter(s => s.has_video)
    } else if (assetFilter === 'complete') {
      filtered = filtered.filter(s => s.has_audio && s.has_video)
    }

    // Genre filter
    if (selectedGenres.length > 0) {
      filtered = filtered.filter(s => selectedGenres.includes(s.genre))
    }

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(s => {
        const searchLower = searchQuery.toLowerCase()
        return (
          s.title?.toLowerCase().includes(searchLower) ||
          s.theme?.toLowerCase().includes(searchLower) ||
          s.parts?.some(p => p.story_text?.toLowerCase().includes(searchLower))
        )
      })
    }

    // Sort
    if (sortBy === 'date') {
      filtered.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    } else if (sortBy === 'title') {
      filtered.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
    } else if (sortBy === 'genre') {
      filtered.sort((a, b) => a.genre.localeCompare(b.genre))
    }

    return filtered
  }

  const handleDeleteSeries = async (seriesId) => {
    if (!confirm('Delete this series? This will remove all associated parts and assets.')) return

    try {
      await axios.delete(`${API_URL}/stories/series/${seriesId}`)
      loadAllContent()
    } catch (error) {
      console.error('Failed to delete series:', error)
      alert('Failed to delete series')
    }
  }

  const handleContinueSeries = (seriesId, seriesData) => {
    navigate('/generator', {
      state: {
        seriesId,
        continueMode: true,
        seriesData  // Pass full series data for immediate loading
      }
    })
  }

  const handleViewDetails = async (seriesData) => {
    setExpandedSeries(seriesData)
  }

  const handleReuseSeries = (seriesData) => {
    if (seriesData.parts && seriesData.parts.length > 0 && onReuseStory) {
      const firstPart = seriesData.parts[0]
      onReuseStory({
        story: firstPart.story_text,
        genre: seriesData.genre,
        word_count: firstPart.word_count
      })
      navigate('/generator')
    }
  }

  const toggleGenreFilter = (genre) => {
    setSelectedGenres(prev =>
      prev.includes(genre) ? prev.filter(g => g !== genre) : [...prev, genre]
    )
  }

  const toggleItemSelection = (itemId) => {
    setSelectedItems(prev =>
      prev.includes(itemId) ? prev.filter(id => id !== itemId) : [...prev, itemId]
    )
  }

  const handleSelectAll = () => {
    setSelectedItems(filteredSeries.map(s => s.story_id))
  }

  const handleDeselectAll = () => {
    setSelectedItems([])
  }

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${selectedItems.length} selected series? This will remove all associated parts and assets.`)) return

    setLoading(true)
    try {
      for (const id of selectedItems) {
        await axios.delete(`${API_URL}/stories/series/${id}`)
      }
      setSelectedItems([])
      setBulkMode(false)
      loadAllContent()
    } catch (error) {
      console.error('Failed to bulk delete:', error)
      alert('Failed to delete some series')
    } finally {
      setLoading(false)
    }
  }

  const filteredSeries = getFilteredSeries()

  const FilterChip = ({ active, onClick, label, count }) => (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
        active
          ? 'bg-primary-600 text-white'
          : 'bg-dark-lighter text-gray-300 hover:bg-dark-hover'
      }`}
    >
      {label}
      {count !== undefined && <span className="ml-1.5 text-sm opacity-75">({count})</span>}
    </button>
  )

  const SeriesCard = ({ s }) => {
    const isMultiPart = s.total_parts > 1
    const isComplete = s.current_part >= s.total_parts
    const progress = s.total_parts > 0 ? (s.current_part / s.total_parts) * 100 : 0

    return (
      <div className="relative bg-dark-lighter border border-dark-border rounded-lg p-5 hover:border-primary-500 transition-colors">
        {bulkMode && (
          <div className="absolute top-3 right-3 z-10">
            <input
              type="checkbox"
              checked={selectedItems.includes(s.story_id)}
              onChange={() => toggleItemSelection(s.story_id)}
              className="w-5 h-5 cursor-pointer"
            />
          </div>
        )}
        {/* Header */}
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1 mr-3">
            <h3 className="font-bold text-lg mb-1 line-clamp-1">{s.title}</h3>
            <div className="flex gap-2 items-center text-sm text-gray-400">
              <span className="px-2 py-0.5 bg-dark-hover rounded text-xs font-medium">
                {s.genre.replace('_', ' ')}
              </span>
              {isMultiPart && (
                <span className="px-2 py-0.5 bg-purple-900 text-purple-300 rounded text-xs font-medium">
                  Series
                </span>
              )}
              <span>{formatDate(s.updated_at)}</span>
            </div>
          </div>
        </div>

        {/* Progress */}
        <div className="mb-3">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-400">
              {isMultiPart ? `Part ${s.current_part}/${s.total_parts}` : 'Single Video'}
            </span>
            {!isComplete && isMultiPart && (
              <span className="text-primary-400 text-xs">In Progress</span>
            )}
            {isComplete && isMultiPart && (
              <span className="text-green-400 text-xs">Complete</span>
            )}
          </div>
          {isMultiPart && (
            <div className="w-full bg-dark-hover rounded-full h-1.5">
              <div
                className={`h-full rounded-full transition-all ${isComplete ? 'bg-green-500' : 'bg-primary-500'}`}
                style={{ width: `${progress}%` }}
              />
            </div>
          )}
        </div>

        {/* Asset Badges */}
        <div className="flex gap-2 mb-4">
          {s.audio_count > 0 && (
            <span className="px-2 py-1 bg-blue-900/30 text-blue-300 rounded text-xs flex items-center gap-1">
              <Music size={12} />
              Audio ({s.audio_count})
            </span>
          )}
          {s.video_count > 0 && (
            <span className="px-2 py-1 bg-green-900/30 text-green-300 rounded text-xs flex items-center gap-1">
              <VideoIcon size={12} />
              Video ({s.video_count})
            </span>
          )}
          {s.parts_count > 0 && (
            <span className="px-2 py-1 bg-gray-700/30 text-gray-300 rounded text-xs flex items-center gap-1">
              <FileText size={12} />
              {s.parts_count} part{s.parts_count > 1 ? 's' : ''}
            </span>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => handleViewDetails(s)}
            className="btn-secondary flex-1 text-sm py-2 flex items-center justify-center gap-1"
          >
            <Eye size={14} />
            View Details
          </button>

          {isMultiPart && !isComplete && (
            <button
              onClick={() => handleContinueSeries(s.story_id, s)}
              className="btn-primary flex-1 text-sm py-2 flex items-center justify-center gap-1"
            >
              <ChevronRight size={14} />
              Continue
            </button>
          )}

          {s.parts?.length > 0 && (
            <button
              onClick={() => handleReuseSeries(s)}
              className="btn-secondary text-sm py-2 px-3"
              title="Reuse in Generator"
            >
              <Play size={14} />
            </button>
          )}

          <button
            onClick={() => handleDeleteSeries(s.story_id)}
            className="btn-secondary text-red-400 hover:bg-red-900/20 text-sm py-2 px-3"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
    )
  }

  const DetailModal = () => {
    if (!expandedSeries) return null

    return (
      <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setExpandedSeries(null)}>
        <div className="bg-dark-lighter border border-dark-border rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div className="sticky top-0 bg-dark-lighter border-b border-dark-border p-6 flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold mb-2">{expandedSeries.title}</h2>
              <div className="flex gap-2 items-center text-sm text-gray-400">
                <span className="px-2 py-0.5 bg-dark-hover rounded">{expandedSeries.genre}</span>
                <span>Theme: {expandedSeries.theme}</span>
                <span>•</span>
                <span>{expandedSeries.parts_count} part{expandedSeries.parts_count > 1 ? 's' : ''}</span>
              </div>
            </div>
            <button
              onClick={() => setExpandedSeries(null)}
              className="text-gray-400 hover:text-white"
            >
              <X size={24} />
            </button>
          </div>

          {/* Parts List */}
          <div className="p-6 space-y-4">
            {expandedSeries.parts?.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No parts generated yet</p>
            ) : (
              expandedSeries.parts?.map((part, idx) => (
                <div key={idx} className="bg-dark-hover border border-dark-border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-bold text-lg">Part {part.part}</h3>
                      <div className="text-sm text-gray-400">
                        {part.word_count} words • {part.duration}s • {formatDate(part.timestamp)}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {part.audio_path && (
                        <span className="px-2 py-1 bg-blue-900/30 text-blue-300 rounded text-xs">
                          <Music size={12} className="inline mr-1" />
                          Audio
                        </span>
                      )}
                      {part.video_path && (
                        <span className="px-2 py-1 bg-green-900/30 text-green-300 rounded text-xs">
                          <VideoIcon size={12} className="inline mr-1" />
                          Video
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Story Text Preview */}
                  <div className="bg-dark rounded p-3 mb-3">
                    <p className="text-sm text-gray-300 line-clamp-3">{part.story_text}</p>
                  </div>

                  {/* Audio Player */}
                  {part.audio_path && (
                    <div className="mb-3">
                      <div className="text-xs text-gray-400 mb-1">Audio:</div>
                      <AudioPlayer src={`${API_URL.replace('/api', '')}/api/files/audio/${part.audio_path}`} />
                    </div>
                  )}

                  {/* Video Player */}
                  {part.video_path && (
                    <div className="mb-3">
                      <div className="text-xs text-gray-400 mb-1">Video:</div>
                      <VideoPlayer src={`${API_URL.replace('/api', '')}/api/files/video/${part.video_path}`} />
                    </div>
                  )}

                  {/* Download Buttons */}
                  <div className="flex gap-2">
                    {part.audio_path && (
                      <a
                        href={`${API_URL.replace('/api', '')}/api/files/audio/${part.audio_path}`}
                        download
                        className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1"
                      >
                        <Download size={12} />
                        Download Audio
                      </a>
                    )}
                    {part.video_path && (
                      <a
                        href={`${API_URL.replace('/api', '')}/api/files/video/${part.video_path}`}
                        download
                        className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1"
                      >
                        <Download size={12} />
                        Download Video
                      </a>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Content Library</h1>
        <p className="text-gray-400">Manage your video series and content</p>
      </div>

      {/* Search & Refresh */}
      <div className="flex gap-3 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search by title, theme, or content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-dark-lighter border border-dark-border rounded-lg focus:border-primary-500 focus:outline-none"
          />
        </div>
        <button
          onClick={loadAllContent}
          disabled={loading}
          className="btn-secondary px-4 flex items-center gap-2"
        >
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
        <button
          onClick={() => {
            setBulkMode(!bulkMode)
            setSelectedItems([])
          }}
          className="btn-secondary px-4 flex items-center gap-2"
        >
          {bulkMode ? <X size={18} /> : <CheckSquare size={18} />}
          {bulkMode ? 'Cancel' : 'Select'}
        </button>
      </div>

      {/* Bulk Actions Bar */}
      {bulkMode && (
        <div className="mb-4 p-4 bg-primary-900/20 border border-primary-500 rounded-lg flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={handleSelectAll}
              className="btn-secondary text-sm"
            >
              Select All ({filteredSeries.length})
            </button>
            <button
              onClick={handleDeselectAll}
              className="btn-secondary text-sm"
            >
              Deselect All
            </button>
            <span className="text-sm text-gray-400">
              {selectedItems.length} selected
            </span>
          </div>
          <button
            onClick={handleBulkDelete}
            disabled={selectedItems.length === 0}
            className="btn-secondary text-red-400 hover:bg-red-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Trash2 size={16} />
            Delete Selected ({selectedItems.length})
          </button>
        </div>
      )}

      {/* Content Filters */}
      <div className="mb-4">
        <div className="text-sm font-medium text-gray-400 mb-2">Content Type</div>
        <div className="flex gap-2 flex-wrap">
          <FilterChip
            active={contentFilter === 'all'}
            onClick={() => setContentFilter('all')}
            label="All"
            count={series.length}
          />
          <FilterChip
            active={contentFilter === 'singles'}
            onClick={() => setContentFilter('singles')}
            label="Singles"
            count={series.filter(s => s.total_parts === 1).length}
          />
          <FilterChip
            active={contentFilter === 'multi-part'}
            onClick={() => setContentFilter('multi-part')}
            label="Multi-Part"
            count={series.filter(s => s.total_parts > 1).length}
          />
        </div>
      </div>

      {/* Asset Filters */}
      <div className="mb-4">
        <div className="text-sm font-medium text-gray-400 mb-2">Assets</div>
        <div className="flex gap-2 flex-wrap">
          <FilterChip
            active={assetFilter === 'all'}
            onClick={() => setAssetFilter('all')}
            label="All"
          />
          <FilterChip
            active={assetFilter === 'with-audio'}
            onClick={() => setAssetFilter('with-audio')}
            label="With Audio"
            count={series.filter(s => s.has_audio).length}
          />
          <FilterChip
            active={assetFilter === 'with-video'}
            onClick={() => setAssetFilter('with-video')}
            label="With Video"
            count={series.filter(s => s.has_video).length}
          />
          <FilterChip
            active={assetFilter === 'complete'}
            onClick={() => setAssetFilter('complete')}
            label="Complete"
            count={series.filter(s => s.has_audio && s.has_video).length}
          />
        </div>
      </div>

      {/* Genre Filters */}
      <div className="mb-4">
        <div className="text-sm font-medium text-gray-400 mb-2">Genre</div>
        <div className="flex gap-2 flex-wrap">
          {genres.map(genre => (
            <FilterChip
              key={genre}
              active={selectedGenres.includes(genre)}
              onClick={() => toggleGenreFilter(genre)}
              label={genre.replace('_', ' ')}
              count={series.filter(s => s.genre === genre).length}
            />
          ))}
        </div>
      </div>

      {/* Sort */}
      <div className="mb-6 flex items-center gap-3">
        <span className="text-sm text-gray-400">Sort by:</span>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-dark-lighter border border-dark-border rounded-lg px-3 py-1.5 text-sm focus:border-primary-500 focus:outline-none"
        >
          <option value="date">Date (newest first)</option>
          <option value="title">Title</option>
          <option value="genre">Genre</option>
        </select>
        <span className="text-sm text-gray-400 ml-auto">
          {filteredSeries.length} series
        </span>
      </div>

      {/* Series Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader className="animate-spin text-primary-500" size={40} />
        </div>
      ) : filteredSeries.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-lg mb-2">No series found</p>
          <p className="text-sm">Try adjusting your filters or create some content in the Generator</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSeries.map((s) => (
            <SeriesCard key={s.story_id} s={s} />
          ))}
        </div>
      )}

      {/* Detail Modal */}
      <DetailModal />
    </div>
  )
}
