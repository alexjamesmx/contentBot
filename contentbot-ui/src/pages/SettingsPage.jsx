import { useState, useEffect } from 'react'
import { Save, Key, Video, CheckCircle, XCircle, Trash2, RefreshCw } from 'lucide-react'
import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

const QUALITY_PRESETS = {
  draft: {
    name: 'Draft',
    desc: 'Fast rendering, lower quality',
    bitrate: '3000k',
    preset: 'faster',
    crf: '23'
  },
  standard: {
    name: 'Standard',
    desc: 'Balanced quality and speed',
    bitrate: '5000k',
    preset: 'medium',
    crf: '21'
  },
  viral: {
    name: 'Viral',
    desc: 'Max quality for TikTok/YT Shorts',
    bitrate: '8000k',
    preset: 'slow',
    crf: '18'
  }
}

export default function SettingsPage() {
  const [config, setConfig] = useState(null)
  const [apiKeys, setApiKeys] = useState({
    GROQ_API_KEY: '',
    ELEVENLABS_API_KEY: ''
  })
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)
  const [cacheSize, setCacheSize] = useState(null)
  const [selectedQuality, setSelectedQuality] = useState('viral')

  useEffect(() => {
    loadConfig()
    loadCacheSize()
  }, [])

  const loadConfig = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/config`)
      if (data.success) {
        setConfig(data.config)
      }
    } catch (error) {
      console.error('Failed to load config:', error)
    }
  }

  const loadCacheSize = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/cache/size`)
      if (data.success) {
        setCacheSize(data.size_mb)
      }
    } catch (error) {
      console.log('Cache info not available')
    }
  }

  const saveSettings = async () => {
    setSaving(true)
    try {
      await axios.post(`${API_URL}/config`, apiKeys)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
      loadConfig()
    } catch (error) {
      console.error('Failed to save settings:', error)
      alert('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const clearCache = async () => {
    if (!confirm('Clear all cached audio files?')) return

    try {
      const { data } = await axios.post(`${API_URL}/cache/clear`)
      if (data.success) {
        alert(`Cleared ${data.files_deleted} cached files`)
        loadCacheSize()
      }
    } catch (error) {
      alert('Failed to clear cache')
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-400">Configure API keys and video quality</p>
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
              <span className="text-sm">Groq API (AI Stories)</span>
              {config?.api_keys.groq ? (
                <div className="flex items-center gap-2">
                  <CheckCircle size={20} className="text-green-400" />
                  <span className="text-xs text-green-400">Connected</span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <XCircle size={20} className="text-red-400" />
                  <span className="text-xs text-red-400">Required</span>
                </div>
              )}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">ElevenLabs (Premium TTS)</span>
              {config?.api_keys.elevenlabs ? (
                <div className="flex items-center gap-2">
                  <CheckCircle size={20} className="text-green-400" />
                  <span className="text-xs text-green-400">Connected</span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <XCircle size={20} className="text-gray-400" />
                  <span className="text-xs text-gray-400">Optional</span>
                </div>
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
              Free tier: 30 req/min • Get key at{' '}
              <a href="https://console.groq.com" target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:underline">
                console.groq.com
              </a>
            </p>
          </div>

          {/* ElevenLabs API Key */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">
              ElevenLabs API Key
              <span className="text-gray-400 ml-1">(Optional)</span>
            </label>
            <input
              type="password"
              value={apiKeys.ELEVENLABS_API_KEY}
              onChange={(e) => setApiKeys({ ...apiKeys, ELEVENLABS_API_KEY: e.target.value })}
              placeholder="Optional - for realistic voices"
              className="input w-full font-mono"
            />
            <p className="text-xs text-gray-400 mt-1">
              Starter: $5/month (30K chars) • Get at{' '}
              <a href="https://elevenlabs.io/pricing" target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:underline">
                elevenlabs.io
              </a>
            </p>
          </div>

          <button
            onClick={saveSettings}
            disabled={saving || !apiKeys.GROQ_API_KEY}
            className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save size={20} />
            {saving ? 'Saving...' : saved ? 'Saved!' : 'Save API Keys'}
          </button>

          {saved && (
            <p className="text-sm text-green-400 mt-2">
              ✓ Settings saved! Restart backend to apply changes.
            </p>
          )}
        </div>

        {/* Video Quality */}
        <div className="card">
          <h3 className="font-bold mb-4 flex items-center gap-2">
            <Video size={20} />
            Video Quality
          </h3>

          <div className="grid grid-cols-3 gap-4 mb-6">
            {Object.entries(QUALITY_PRESETS).map(([key, preset]) => (
              <div
                key={key}
                onClick={() => setSelectedQuality(key)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  key === selectedQuality
                    ? 'border-primary-500 bg-primary-500/10'
                    : 'border-dark-border bg-dark-hover hover:border-primary-500/50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{preset.name}</span>
                  {key === selectedQuality && (
                    <span className="text-xs bg-primary-500 text-white px-2 py-0.5 rounded">
                      Selected
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-400">{preset.desc}</p>
                <div className="mt-2 text-xs text-gray-500 space-y-1">
                  <div>Bitrate: {preset.bitrate}</div>
                  <div>Preset: {preset.preset}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Current Specs */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-dark-hover rounded-lg">
            <div>
              <span className="text-xs text-gray-400">Resolution</span>
              <p className="text-sm font-medium">
                {config?.video.width || 1080}x{config?.video.height || 1920}
                <span className="text-xs text-gray-400 ml-2">(9:16 vertical)</span>
              </p>
            </div>
            <div>
              <span className="text-xs text-gray-400">Frame Rate</span>
              <p className="text-sm font-medium">{config?.video.fps || 30} FPS</p>
            </div>
            <div>
              <span className="text-xs text-gray-400">Video Bitrate</span>
              <p className="text-sm font-medium">{QUALITY_PRESETS[selectedQuality].bitrate}</p>
            </div>
            <div>
              <span className="text-xs text-gray-400">Encoding Preset</span>
              <p className="text-sm font-medium capitalize">{QUALITY_PRESETS[selectedQuality].preset}</p>
            </div>
          </div>

          <div className="flex items-center justify-between mt-4">
            <p className="text-xs text-gray-400">
              {selectedQuality === 'viral' && '✓ Optimized for TikTok Creator Rewards & YouTube Shorts'}
              {selectedQuality === 'standard' && 'Balanced quality - good for testing'}
              {selectedQuality === 'draft' && 'Fast renders - use for quick previews'}
            </p>
            <button
              onClick={async () => {
                try {
                  await axios.post(`${API_URL}/config/quality`, { quality: selectedQuality })
                  alert('Quality preset saved! Restart backend to apply.')
                } catch (error) {
                  alert('Failed to save quality preset')
                }
              }}
              className="btn-primary text-sm px-4 py-2"
            >
              Apply Preset
            </button>
          </div>
        </div>

        {/* Cache Management */}
        <div className="card">
          <h3 className="font-bold mb-4">Cache Management</h3>

          <div className="flex items-center justify-between p-4 bg-dark-hover rounded-lg mb-4">
            <div>
              <p className="text-sm font-medium">Audio Cache</p>
              <p className="text-xs text-gray-400 mt-1">
                Cached ElevenLabs audio to save API costs
              </p>
            </div>
            <div className="text-right">
              {cacheSize !== null ? (
                <>
                  <p className="text-sm font-medium">{cacheSize.toFixed(1)} MB</p>
                  <button
                    onClick={clearCache}
                    className="text-xs text-red-400 hover:underline flex items-center gap-1 mt-1"
                  >
                    <Trash2 size={12} />
                    Clear Cache
                  </button>
                </>
              ) : (
                <span className="text-sm text-gray-400">No cache</span>
              )}
            </div>
          </div>

          <p className="text-xs text-gray-400">
            Tip: Clear cache if voices sound outdated or use different settings
          </p>
        </div>
      </div>
    </div>
  )
}
