import { useState, useEffect } from 'react'
import { Save, Eye, Check, AlertCircle } from 'lucide-react'
import axios from 'axios'

export default function SubtitleConfig() {
  const [config, setConfig] = useState({
    fontSize: 80,
    fontColor: '#FFFF00',
    strokeColor: '#000000',
    strokeWidth: 3,
    wordsPerChunk: 4,
    position: 'bottom',
    fontFamily: 'Montserrat-Bold'
  })

  const [previewText] = useState('This is how your subtitles will look')
  const [loading, setLoading] = useState(false)
  const [saveStatus, setSaveStatus] = useState(null)

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/subtitles/config')
      if (response.data.success) {
        setConfig(response.data.config)
      }
    } catch (error) {
      console.error('Failed to load config:', error)
    }
  }

  const saveConfig = async () => {
    setLoading(true)
    setSaveStatus(null)
    try {
      const response = await axios.post('http://localhost:5000/api/subtitles/config', config)
      if (response.data.success) {
        setSaveStatus('success')
        setTimeout(() => setSaveStatus(null), 3000)
      }
    } catch (error) {
      console.error('Failed to save config:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus(null), 3000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Subtitle Configuration</h1>
        <p className="text-gray-400">Customize subtitle appearance and timing</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Settings Panel */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="font-bold mb-4">Appearance</h3>

            {/* Font Size */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">
                Font Size: {config.fontSize}px
              </label>
              <input
                type="range"
                min="40"
                max="120"
                value={config.fontSize}
                onChange={(e) => setConfig({ ...config, fontSize: parseInt(e.target.value) })}
                className="w-full"
              />
            </div>

            {/* Font Color */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Font Color</label>
              <div className="flex gap-3">
                <input
                  type="color"
                  value={config.fontColor}
                  onChange={(e) => setConfig({ ...config, fontColor: e.target.value })}
                  className="w-16 h-16 rounded-lg cursor-pointer"
                />
                <div className="flex-1">
                  <input
                    type="text"
                    value={config.fontColor}
                    onChange={(e) => setConfig({ ...config, fontColor: e.target.value })}
                    className="input w-full"
                  />
                  <p className="text-xs text-gray-400 mt-1">Hex color code</p>
                </div>
              </div>
            </div>

            {/* Stroke Color */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Stroke Color</label>
              <div className="flex gap-3">
                <input
                  type="color"
                  value={config.strokeColor}
                  onChange={(e) => setConfig({ ...config, strokeColor: e.target.value })}
                  className="w-16 h-16 rounded-lg cursor-pointer"
                />
                <div className="flex-1">
                  <input
                    type="text"
                    value={config.strokeColor}
                    onChange={(e) => setConfig({ ...config, strokeColor: e.target.value })}
                    className="input w-full"
                  />
                  <p className="text-xs text-gray-400 mt-1">Outline color</p>
                </div>
              </div>
            </div>

            {/* Stroke Width */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">
                Stroke Width: {config.strokeWidth}px
              </label>
              <input
                type="range"
                min="0"
                max="8"
                value={config.strokeWidth}
                onChange={(e) => setConfig({ ...config, strokeWidth: parseInt(e.target.value) })}
                className="w-full"
              />
            </div>

            {/* Font Family */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Font Family</label>
              <select
                value={config.fontFamily}
                onChange={(e) => setConfig({ ...config, fontFamily: e.target.value })}
                className="input w-full"
              >
                <option value="Montserrat-Bold">Montserrat Bold (Recommended - 60% of viral videos)</option>
                <option value="Impact">Impact</option>
                <option value="Arial-Bold">Arial Bold</option>
                <option value="Bebas-Neue">Bebas Neue</option>
                <option value="Anton">Anton</option>
              </select>
            </div>
          </div>

          <div className="card">
            <h3 className="font-bold mb-4">Timing</h3>

            {/* Words Per Chunk */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">
                Words Per Chunk: {config.wordsPerChunk}
                {config.wordsPerChunk >= 3 && config.wordsPerChunk <= 5 && (
                  <span className="ml-2 text-xs text-green-400">✓ Optimal</span>
                )}
              </label>
              <input
                type="range"
                min="1"
                max="6"
                value={config.wordsPerChunk}
                onChange={(e) => setConfig({ ...config, wordsPerChunk: parseInt(e.target.value) })}
                className="w-full"
              />
              <p className="text-xs text-gray-400 mt-1">3-5 words = most viral (2025 research)</p>
            </div>

            {/* Position */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Position</label>
              <select
                value={config.position}
                onChange={(e) => setConfig({ ...config, position: e.target.value })}
                className="input w-full"
              >
                <option value="top">Top</option>
                <option value="center">Center</option>
                <option value="bottom">Bottom (Recommended for 9:16)</option>
              </select>
            </div>
          </div>

          <button
            onClick={saveConfig}
            disabled={loading}
            className={`btn-primary w-full flex items-center justify-center gap-2 ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {saveStatus === 'success' ? (
              <>
                <Check size={20} />
                Saved Successfully!
              </>
            ) : saveStatus === 'error' ? (
              <>
                <AlertCircle size={20} />
                Save Failed
              </>
            ) : (
              <>
                <Save size={20} />
                {loading ? 'Saving...' : 'Save Configuration'}
              </>
            )}
          </button>
        </div>

        {/* Preview Panel */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="font-bold mb-4 flex items-center gap-2">
              <Eye size={20} />
              Live Preview
            </h3>

            {/* Mock video preview */}
            <div className="aspect-[9/16] bg-gradient-to-br from-purple-900 via-blue-900 to-teal-900 rounded-lg flex items-center justify-center relative overflow-hidden">
              {/* Animated background */}
              <div className="absolute inset-0 opacity-20">
                <div className="absolute w-64 h-64 bg-white rounded-full -top-32 -left-32 animate-pulse"></div>
                <div className="absolute w-48 h-48 bg-white rounded-full -bottom-24 -right-24 animate-pulse" style={{ animationDelay: '1s' }}></div>
              </div>

              {/* Subtitle preview */}
              <div
                className="relative z-10 text-center px-8"
                style={{
                  fontSize: `${config.fontSize}px`,
                  color: config.fontColor,
                  fontFamily: config.fontFamily,
                  textShadow: `
                    -${config.strokeWidth}px -${config.strokeWidth}px 0 ${config.strokeColor},
                    ${config.strokeWidth}px -${config.strokeWidth}px 0 ${config.strokeColor},
                    -${config.strokeWidth}px ${config.strokeWidth}px 0 ${config.strokeColor},
                    ${config.strokeWidth}px ${config.strokeWidth}px 0 ${config.strokeColor}
                  `,
                  fontWeight: 'bold',
                  lineHeight: 1.2
                }}
              >
                {previewText}
              </div>
            </div>

            <p className="text-xs text-gray-400 mt-3 text-center">
              Preview updates in real-time as you adjust settings
            </p>
          </div>

          <div className="card bg-blue-900 bg-opacity-20 border-blue-800">
            <h4 className="font-bold text-blue-400 mb-2">💡 Viral Subtitle Tips</h4>
            <ul className="text-sm text-blue-300 space-y-2">
              <li>• Yellow text (#FFFF00) gets 30% more retention</li>
              <li>• 2-3 words per chunk keeps viewers hooked</li>
              <li>• Center position works best for 9:16 videos</li>
              <li>• Bold fonts (Impact, Bebas) increase readability</li>
              <li>• Black stroke ensures visibility on any background</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
