import { useState, useEffect } from 'react'
import { Play, Download, Trash2, Loader, RefreshCw, Search, Filter, Edit2, Copy, Grid, List, ChevronDown, CheckSquare, Square } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import AudioPlayer from '../components/AudioPlayer'
import VideoPlayer from '../components/VideoPlayer'

const API_URL = 'http://localhost:5000/api'

export default function Library({ onReuseStory, onReuseAudio }) {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('stories')
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState('grid')

  const [stories, setStories] = useState([])
  const [audios, setAudios] = useState([])
  const [videos, setVideos] = useState([])

  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedGenres, setSelectedGenres] = useState([])
  const [wordCountRange, setWordCountRange] = useState([0, 300])
  const [sortBy, setSortBy] = useState('date')
  const [showFilters, setShowFilters] = useState(false)

  // Bulk selection
  const [selectedItems, setSelectedItems] = useState([])
  const [bulkMode, setBulkMode] = useState(false)

  // Edit modal
  const [editingStory, setEditingStory] = useState(null)
  const [editContent, setEditContent] = useState('')

  const genres = ['comedy', 'terror', 'aita', 'genz_chaos', 'relationship_drama']

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

  // Filter and search logic
  const getFilteredStories = () => {
    let filtered = [...stories]

    if (searchQuery) {
      filtered = filtered.filter(s =>
        s.story.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (s.title && s.title.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    }

    if (selectedGenres.length > 0) {
      filtered = filtered.filter(s => selectedGenres.includes(s.genre))
    }

    if (wordCountRange[0] > 0 || wordCountRange[1] < 300) {
      filtered = filtered.filter(s =>
        s.word_count >= wordCountRange[0] && s.word_count <= wordCountRange[1]
      )
    }

    // Sort
    if (sortBy === 'date') {
      filtered.sort((a, b) => b.created_at - a.created_at)
    } else if (sortBy === 'words') {
      filtered.sort((a, b) => b.word_count - a.word_count)
    } else if (sortBy === 'genre') {
      filtered.sort((a, b) => a.genre.localeCompare(b.genre))
    }

    return filtered
  }

  const handleDeleteStory = async (storyId) => {
    if (!confirm('Delete this story?')) return
    try {
      await axios.delete(`${API_URL}/stories/${storyId}`)
      loadContent()
    } catch (error) {
      console.error('Failed to delete story:', error)
    }
  }

  const handleDuplicateStory = async (story) => {
    try {
      await axios.post(`${API_URL}/stories`, {
        ...story,
        id: undefined,
        title: (story.title || 'Untitled') + ' (Copy)',
        created_at: Date.now() / 1000
      })
      loadContent()
    } catch (error) {
      console.error('Failed to duplicate story:', error)
    }
  }

  const handleEditStory = (story) => {
    setEditingStory(story)
    setEditContent(story.story)
  }

  const handleSaveEdit = async () => {
    try {
      await axios.put(`${API_URL}/stories/${editingStory.id}`, {
        ...editingStory,
        story: editContent,
        word_count: editContent.split(' ').length
      })
      setEditingStory(null)
      loadContent()
    } catch (error) {
      console.error('Failed to save story:', error)
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

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${selectedItems.length} selected items?`)) return
    try {
      for (const id of selectedItems) {
        await axios.delete(`${API_URL}/stories/${id}`)
      }
      setSelectedItems([])
      setBulkMode(false)
      loadContent()
    } catch (error) {
      console.error('Failed to bulk delete:', error)
    }
  }

  const handleBulkExport = () => {
    const selected = stories.filter(s => selectedItems.includes(s.id))
    const dataStr = JSON.stringify(selected, null, 2)
    const blob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `stories_export_${Date.now()}.json`
    link.click()
  }

  const filteredStories = getFilteredStories()

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Content Library</h1>
        <p className="text-gray-400">Manage and reuse your generated content</p>
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

      {/* Search and Filters - Stories Only */}
      {activeTab === 'stories' && (
        <div className="mb-6 space-y-4">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search stories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input w-full pl-10"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`btn-secondary flex items-center gap-2 ${showFilters ? 'bg-primary-900 bg-opacity-20 border-primary-800' : ''}`}
            >
              <Filter size={18} />
              Filters
              <ChevronDown size={16} className={`transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>
            <button
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className="btn-secondary flex items-center gap-2"
            >
              {viewMode === 'grid' ? <List size={18} /> : <Grid size={18} />}
            </button>
            <button
              onClick={() => setBulkMode(!bulkMode)}
              className={`btn-secondary flex items-center gap-2 ${bulkMode ? 'bg-primary-900 bg-opacity-20 border-primary-800' : ''}`}
            >
              <CheckSquare size={18} />
              Bulk
            </button>
          </div>

          {showFilters && (
            <div className="card p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Genres</label>
                <div className="flex flex-wrap gap-2">
                  {genres.map(genre => (
                    <button
                      key={genre}
                      onClick={() => toggleGenreFilter(genre)}
                      className={`px-3 py-1 rounded-lg text-sm capitalize ${
                        selectedGenres.includes(genre)
                          ? 'bg-primary-600 text-white'
                          : 'bg-dark-hover text-gray-400 hover:bg-dark-border'
                      }`}
                    >
                      {genre.replace('_', ' ')}
                    </button>
                  ))}
                  {selectedGenres.length > 0 && (
                    <button
                      onClick={() => setSelectedGenres([])}
                      className="px-3 py-1 rounded-lg text-sm text-red-400 hover:bg-red-900 hover:bg-opacity-20"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Word Count: {wordCountRange[0]} - {wordCountRange[1]} words
                </label>
                <div className="flex gap-4">
                  <input
                    type="range"
                    min="0"
                    max="300"
                    value={wordCountRange[0]}
                    onChange={(e) => setWordCountRange([parseInt(e.target.value), wordCountRange[1]])}
                    className="flex-1"
                  />
                  <input
                    type="range"
                    min="0"
                    max="300"
                    value={wordCountRange[1]}
                    onChange={(e) => setWordCountRange([wordCountRange[0], parseInt(e.target.value)])}
                    className="flex-1"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Sort By</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="input w-full"
                >
                  <option value="date">Date (Newest First)</option>
                  <option value="words">Word Count (Highest First)</option>
                  <option value="genre">Genre (A-Z)</option>
                </select>
              </div>
            </div>
          )}

          {bulkMode && selectedItems.length > 0 && (
            <div className="card p-4 bg-primary-900 bg-opacity-20 border-primary-800">
              <div className="flex items-center justify-between">
                <p className="text-sm">
                  <strong>{selectedItems.length}</strong> items selected
                </p>
                <div className="flex gap-2">
                  <button onClick={handleBulkExport} className="btn-secondary text-sm">
                    Export JSON
                  </button>
                  <button onClick={handleBulkDelete} className="btn-secondary text-sm text-red-400 hover:bg-red-900">
                    Delete All
                  </button>
                  <button onClick={() => setSelectedItems([])} className="btn-secondary text-sm">
                    Clear Selection
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="animate-spin" size={32} />
        </div>
      ) : (
        <>
          {/* Stories Tab */}
          {activeTab === 'stories' && (
            <>
              {filteredStories.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  {stories.length === 0 ? 'No stories yet. Generate your first story!' : 'No stories match your filters.'}
                </div>
              ) : viewMode === 'grid' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredStories.map((story) => (
                    <div key={story.id} className="card relative">
                      {bulkMode && (
                        <button
                          onClick={() => toggleItemSelection(story.id)}
                          className="absolute top-3 right-3 z-10"
                        >
                          {selectedItems.includes(story.id) ? (
                            <CheckSquare size={20} className="text-primary-400" />
                          ) : (
                            <Square size={20} className="text-gray-400" />
                          )}
                        </button>
                      )}
                      <div className="mb-3">
                        <h3 className="font-bold text-sm mb-1 line-clamp-1">{story.title || 'Untitled Story'}</h3>
                        <p className="text-xs text-gray-400 capitalize">
                          {story.genre.replace('_', ' ')} • {story.word_count} words
                        </p>
                        <p className="text-xs text-gray-500">{formatDate(story.created_at)}</p>
                      </div>
                      <p className="text-sm text-gray-300 line-clamp-4 mb-3">{story.story}</p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            onReuseStory && onReuseStory(story)
                            navigate('/generator')
                          }}
                          className="btn-primary flex-1 text-xs py-1"
                        >
                          Use
                        </button>
                        <button
                          onClick={() => handleEditStory(story)}
                          className="btn-secondary text-xs py-1 px-2"
                        >
                          <Edit2 size={14} />
                        </button>
                        <button
                          onClick={() => handleDuplicateStory(story)}
                          className="btn-secondary text-xs py-1 px-2"
                        >
                          <Copy size={14} />
                        </button>
                        <button
                          onClick={() => handleDeleteStory(story.id)}
                          className="btn-secondary text-xs py-1 px-2 text-red-400 hover:bg-red-900"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredStories.map((story) => (
                    <div key={story.id} className="card">
                      <div className="flex items-start gap-4">
                        {bulkMode && (
                          <button
                            onClick={() => toggleItemSelection(story.id)}
                            className="mt-1"
                          >
                            {selectedItems.includes(story.id) ? (
                              <CheckSquare size={20} className="text-primary-400" />
                            ) : (
                              <Square size={20} className="text-gray-400" />
                            )}
                          </button>
                        )}
                        <div className="flex-1">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h3 className="font-bold">{story.title || 'Untitled Story'}</h3>
                              <p className="text-sm text-gray-400 capitalize">
                                {story.genre.replace('_', ' ')} • {story.word_count} words • {formatDate(story.created_at)}
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <button
                                onClick={() => {
                                  onReuseStory && onReuseStory(story)
                                  navigate('/generator')
                                }}
                                className="btn-primary flex items-center gap-2 text-sm"
                              >
                                <RefreshCw size={14} />
                                Use
                              </button>
                              <button
                                onClick={() => handleEditStory(story)}
                                className="btn-secondary px-2"
                              >
                                <Edit2 size={16} />
                              </button>
                              <button
                                onClick={() => handleDuplicateStory(story)}
                                className="btn-secondary px-2"
                              >
                                <Copy size={16} />
                              </button>
                              <button
                                onClick={() => handleDeleteStory(story.id)}
                                className="btn-secondary px-2 text-red-400 hover:bg-red-900"
                              >
                                <Trash2 size={16} />
                              </button>
                            </div>
                          </div>
                          <p className="text-gray-300 line-clamp-2">{story.story}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
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

      {/* Edit Modal */}
      {editingStory && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-dark-bg border border-dark-border rounded-lg max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-dark-border">
              <h2 className="text-xl font-bold">Edit Story</h2>
              <p className="text-sm text-gray-400 mt-1">
                {editContent.split(' ').length} words • ~{Math.ceil(editContent.split(' ').length / 2.5)}s
              </p>
            </div>
            <div className="p-6 flex-1 overflow-y-auto">
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="input w-full h-96 resize-none font-mono text-sm"
                autoFocus
              />
            </div>
            <div className="p-6 border-t border-dark-border flex gap-3 justify-end">
              <button onClick={() => setEditingStory(null)} className="btn-secondary">
                Cancel
              </button>
              <button onClick={handleSaveEdit} className="btn-primary">
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
