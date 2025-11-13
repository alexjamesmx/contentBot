import { useState, useEffect } from 'react'
import { Upload, Trash2, Play, Folder, Eye, X } from 'lucide-react'
import axios from 'axios'
import VideoPlayer from '../components/VideoPlayer'

export default function MediaManager() {
  const [backgrounds, setBackgrounds] = useState([])
  const [uploading, setUploading] = useState(false)
  const [previewVideo, setPreviewVideo] = useState(null)

  useEffect(() => {
    loadBackgrounds()
  }, [])

  const loadBackgrounds = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/files/backgrounds')
      if (response.data.success) {
        setBackgrounds(response.data.backgrounds)
      }
    } catch (error) {
      console.error('Failed to load backgrounds:', error)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      await axios.post('http://localhost:5000/api/files/backgrounds', formData)
      loadBackgrounds()
    } catch (error) {
      console.error('Failed to upload file:', error)
      alert('Failed to upload file')
    } finally {
      setUploading(false)
    }
  }

  const deleteBackground = async (filename) => {
    if (!confirm(`Delete ${filename}?`)) return

    try {
      await axios.delete(`http://localhost:5000/api/files/backgrounds/${filename}`)
      loadBackgrounds()
    } catch (error) {
      console.error('Failed to delete file:', error)
      alert('Failed to delete file')
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Media Manager</h1>
        <p className="text-gray-400">Manage background videos, fonts, and music</p>
      </div>

      {/* Upload Section */}
      <div className="card mb-6">
        <h3 className="font-bold mb-4">Upload Background Video</h3>
        <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-dark-border rounded-lg cursor-pointer hover:border-primary-500 transition-colors">
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <Upload size={48} className="mb-3 text-gray-400" />
            <p className="mb-2 text-sm text-gray-400">
              <span className="font-semibold">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">MP4, MOV (MAX. 100MB)</p>
          </div>
          <input
            type="file"
            className="hidden"
            accept="video/mp4,video/quicktime"
            onChange={handleFileUpload}
            disabled={uploading}
          />
        </label>
      </div>

      {/* Background Videos Grid */}
      <div className="card">
        <h3 className="font-bold mb-4">Background Videos ({backgrounds.length})</h3>
        {backgrounds.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <Folder size={48} className="mx-auto mb-4 opacity-50" />
            <p>No background videos uploaded</p>
            <p className="text-sm mt-2">Upload videos to use in your Shorts</p>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {backgrounds.map((bg, index) => (
              <div
                key={index}
                className="bg-dark-hover rounded-lg p-4 hover:bg-opacity-80 transition-colors"
              >
                <div
                  className="aspect-video bg-dark-bg rounded-lg mb-3 flex items-center justify-center cursor-pointer group relative overflow-hidden"
                  onClick={() => setPreviewVideo(bg)}
                >
                  <Play size={32} className="text-gray-600 group-hover:text-primary-400 transition-colors" />
                  <div className="absolute inset-0 bg-primary-600 opacity-0 group-hover:opacity-10 transition-opacity"></div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate text-sm">{bg.name}</p>
                    <p className="text-xs text-gray-400">
                      {(bg.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setPreviewVideo(bg)}
                      className="p-2 hover:bg-primary-900 hover:bg-opacity-30 rounded-lg transition-colors"
                    >
                      <Eye size={16} className="text-primary-400" />
                    </button>
                    <button
                      onClick={() => deleteBackground(bg.name)}
                      className="p-2 hover:bg-red-900 hover:bg-opacity-30 rounded-lg transition-colors"
                    >
                      <Trash2 size={16} className="text-red-400" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Video Preview Modal */}
      {previewVideo && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8">
          <div className="bg-dark-card rounded-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
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
                src={`http://localhost:5000/api/files/background/${previewVideo.name}`}
                className="mb-4"
              />

              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-gray-400">Filename</p>
                  <p className="font-medium truncate">{previewVideo.name}</p>
                </div>
                <div>
                  <p className="text-gray-400">Size</p>
                  <p className="font-medium">{(previewVideo.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
                <div>
                  <p className="text-gray-400">Modified</p>
                  <p className="font-medium">
                    {new Date(previewVideo.modified * 1000).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
