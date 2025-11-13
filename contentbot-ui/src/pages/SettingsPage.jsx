import { useState, useEffect } from 'react'
import { Save, Key, Video, Cpu, CheckCircle, XCircle, Eye, EyeOff } from 'lucide-react'
import axios from 'axios'

export default function SettingsPage() {
  const [config, setConfig] = useState(null)
  const [apiKeys, setApiKeys] = useState({
    GROQ_API_KEY: '',
    ELEVENLABS_API_KEY: '',
    REDDIT_CLIENT_ID: '',
    REDDIT_CLIENT_SECRET: ''
  })
  const [saved, setSaved] = useState(false)
  const [showKeys, setShowKeys] = useState({
    GROQ_API_KEY: false,
    ELEVENLABS_API_KEY: false,
    REDDIT_CLIENT_SECRET: false
  })

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/config')
      if (response.data.success) {
        setConfig(response.data.config)
      }
    } catch (error) {
      console.error('Failed to load config:', error)
    }
  }

  const toggleShowKey = (keyName) => {
    setShowKeys(prev => ({ ...prev, [keyName]: !prev[keyName] }))
  }

  const saveSettings = async () => {
    try {
      await axios.post('http://localhost:5000/api/config', apiKeys)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
      loadConfig()
    } catch (error) {
      console.error('Failed to save settings:', error)
      alert('Failed to save settings')
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-400">Configure API keys and video settings</p>
      </div>

      <div className="max-w-4xl space-y-6">
        {/* API Keys */}
        <div className="card">
          <h3 className="font-bold mb-4 flex items-center gap-2">
            <Key size={20} />
            API Keys
          </h3>

          {/* API Status */}
          <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-dark-hover rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm">Groq API</span>
              {config?.api_keys.groq ? (
                <CheckCircle size={20} className="text-green-400" />
              ) : (
                <XCircle size={20} className="text-red-400" />
              )}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">ElevenLabs API</span>
              {config?.api_keys.elevenlabs ? (
                <CheckCircle size={20} className="text-green-400" />
              ) : (
                <XCircle size={20} className="text-red-400" />
              )}
            </div>
          </div>

          {/* Groq API Key */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              Groq API Key
              <span className="text-red-400 ml-1">*</span>
            </label>
            <input
              type="password"
              value={apiKeys.GROQ_API_KEY}
              onChange={(e) => setApiKeys({ ...apiKeys, GROQ_API_KEY: e.target.value })}
              placeholder="gsk_..."
              className="input w-full font-mono"
            />
            <p className="text-xs text-gray-400 mt-1">
              Required for AI story generation • Get free key at{' '}
              <a href="https://console.groq.com" target="_blank" className="text-primary-400 hover:underline">
                console.groq.com
              </a>
            </p>
          </div>

          {/* ElevenLabs API Key */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">ElevenLabs API Key</label>
            <input
              type="password"
              value={apiKeys.ELEVENLABS_API_KEY}
              onChange={(e) => setApiKeys({ ...apiKeys, ELEVENLABS_API_KEY: e.target.value })}
              placeholder="Optional - for premium TTS"
              className="input w-full font-mono"
            />
            <p className="text-xs text-gray-400 mt-1">
              Optional but recommended • $5/month plan • Get at{' '}
              <a href="https://elevenlabs.io" target="_blank" className="text-primary-400 hover:underline">
                elevenlabs.io
              </a>
            </p>
          </div>

          {/* Reddit API Keys */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Reddit Client ID</label>
            <input
              type="text"
              value={apiKeys.REDDIT_CLIENT_ID}
              onChange={(e) => setApiKeys({ ...apiKeys, REDDIT_CLIENT_ID: e.target.value })}
              placeholder="Optional - for Reddit scraping"
              className="input w-full font-mono"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Reddit Client Secret</label>
            <input
              type="password"
              value={apiKeys.REDDIT_CLIENT_SECRET}
              onChange={(e) => setApiKeys({ ...apiKeys, REDDIT_CLIENT_SECRET: e.target.value })}
              placeholder="Optional - for Reddit scraping"
              className="input w-full font-mono"
            />
            <p className="text-xs text-gray-400 mt-1">
              See CLAUDE.md in project root for Reddit API setup guide
            </p>
          </div>

          <button
            onClick={saveSettings}
            className="btn-primary flex items-center gap-2"
          >
            <Save size={20} />
            {saved ? 'Saved!' : 'Save API Keys'}
          </button>
        </div>

        {/* Video Settings */}
        <div className="card">
          <h3 className="font-bold mb-4 flex items-center gap-2">
            <Video size={20} />
            Video Configuration
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Resolution</label>
              <input
                type="text"
                value={`${config?.video.width || 1080}x${config?.video.height || 1920}`}
                readOnly
                className="input w-full bg-dark-bg cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Frame Rate</label>
              <input
                type="text"
                value={`${config?.video.fps || 30} FPS`}
                readOnly
                className="input w-full bg-dark-bg cursor-not-allowed"
              />
            </div>
          </div>

          <p className="text-xs text-gray-400 mt-3">
            Video settings are optimized for TikTok/Instagram Reels/YouTube Shorts
          </p>
        </div>

        {/* AI Settings */}
        <div className="card">
          <h3 className="font-bold mb-4 flex items-center gap-2">
            <Cpu size={20} />
            AI Configuration
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Temperature</label>
              <input
                type="text"
                value={config?.story.temperature || 0.9}
                readOnly
                className="input w-full bg-dark-bg cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Max Tokens</label>
              <input
                type="text"
                value={config?.story.max_tokens || 500}
                readOnly
                className="input w-full bg-dark-bg cursor-not-allowed"
              />
            </div>
          </div>

          <p className="text-xs text-gray-400 mt-3">
            Advanced settings can be edited in .env file
          </p>
        </div>

        {/* Asset Status */}
        <div className="card">
          <h3 className="font-bold mb-4">Asset Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-dark-hover rounded-lg">
              <span className="text-sm">Background Videos</span>
              <span className="text-sm font-medium">{config?.assets.backgrounds.length || 0} files</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-dark-hover rounded-lg">
              <span className="text-sm">Fonts</span>
              <span className="text-sm font-medium">{config?.assets.fonts.length || 0} files</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
