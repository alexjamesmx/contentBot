import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import { Home, Settings, FileVideo, Type, Image, BarChart3, Sparkles } from 'lucide-react'

// Pages
import Dashboard from './pages/Dashboard'
import Generator from './pages/Generator'
import Templates from './pages/Templates'
import MediaManager from './pages/MediaManager'
import SubtitleConfig from './pages/SubtitleConfig'
import SettingsPage from './pages/SettingsPage'
import Analytics from './pages/Analytics'

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-dark-bg">
        {/* Sidebar */}
        <aside className="w-64 bg-dark-card border-r border-dark-border flex flex-col">
          {/* Logo */}
          <div className="p-6 border-b border-dark-border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold">ContentBot</h1>
                <p className="text-xs text-gray-400">Pro Edition</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            <NavItem to="/" icon={<Home size={20} />} label="Dashboard" />
            <NavItem to="/generator" icon={<FileVideo size={20} />} label="Generator" />
            <NavItem to="/templates" icon={<Type size={20} />} label="Templates" />
            <NavItem to="/media" icon={<Image size={20} />} label="Media" />
            <NavItem to="/subtitles" icon={<Type size={20} />} label="Subtitles" />
            <NavItem to="/analytics" icon={<BarChart3 size={20} />} label="Analytics" />
            <NavItem to="/settings" icon={<Settings size={20} />} label="Settings" />
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-dark-border text-xs text-gray-500">
            <p>Version 1.0.0</p>
            <p className="mt-1">© 2025 ContentBot</p>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/generator" element={<Generator />} />
            <Route path="/templates" element={<Templates />} />
            <Route path="/media" element={<MediaManager />} />
            <Route path="/subtitles" element={<SubtitleConfig />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

function NavItem({ to, icon, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
          isActive
            ? 'bg-primary-600 text-white'
            : 'text-gray-400 hover:bg-dark-hover hover:text-white'
        }`
      }
    >
      {icon}
      <span className="font-medium">{label}</span>
    </NavLink>
  )
}

export default App
