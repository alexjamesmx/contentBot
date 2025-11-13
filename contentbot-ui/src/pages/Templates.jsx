import { useState, useEffect } from 'react'
import { Save, RefreshCw, Edit } from 'lucide-react'
import axios from 'axios'

export default function Templates() {
  const [templates, setTemplates] = useState({})
  const [selectedGenre, setSelectedGenre] = useState('comedy')
  const [editMode, setEditMode] = useState(false)
  const [currentTemplate, setCurrentTemplate] = useState(null)

  useEffect(() => {
    loadTemplates()
  }, [])

  useEffect(() => {
    if (templates[selectedGenre]) {
      setCurrentTemplate({ ...templates[selectedGenre] })
    }
  }, [selectedGenre, templates])

  const loadTemplates = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/templates')
      if (response.data.success) {
        setTemplates(response.data.templates)
      }
    } catch (error) {
      console.error('Failed to load templates:', error)
    }
  }

  const saveTemplate = async () => {
    try {
      await axios.put(`http://localhost:5000/api/templates/${selectedGenre}`, currentTemplate)
      setEditMode(false)
      loadTemplates()
    } catch (error) {
      console.error('Failed to save template:', error)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Story Templates</h1>
          <p className="text-gray-400">Customize prompts and hooks for each genre</p>
        </div>
        <button
          onClick={() => setEditMode(!editMode)}
          className="btn-secondary flex items-center gap-2"
        >
          <Edit size={20} />
          {editMode ? 'Cancel' : 'Edit Mode'}
        </button>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/* Genre Selector */}
        <div className="col-span-1">
          <div className="card">
            <h3 className="font-bold mb-4">Genres</h3>
            <div className="space-y-2">
              {Object.keys(templates).map(genre => (
                <button
                  key={genre}
                  onClick={() => setSelectedGenre(genre)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    selectedGenre === genre
                      ? 'bg-primary-600 text-white'
                      : 'bg-dark-hover text-gray-400 hover:text-white'
                  }`}
                >
                  {templates[genre]?.name || genre}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Template Editor */}
        <div className="col-span-3 space-y-6">
          {currentTemplate && (
            <>
              {/* System Prompt */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold">System Prompt</h3>
                  {editMode && (
                    <button onClick={saveTemplate} className="btn-primary flex items-center gap-2">
                      <Save size={16} />
                      Save Changes
                    </button>
                  )}
                </div>
                <textarea
                  value={currentTemplate.system_prompt || ''}
                  onChange={(e) =>
                    setCurrentTemplate({ ...currentTemplate, system_prompt: e.target.value })
                  }
                  disabled={!editMode}
                  className="input w-full h-48 resize-none font-mono text-sm"
                  placeholder="Enter system prompt..."
                />
              </div>

              {/* Hook Patterns */}
              <div className="card">
                <h3 className="font-bold mb-4">Hook Patterns</h3>
                <div className="space-y-3">
                  {currentTemplate.hook_patterns?.map((hook, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <input
                        value={hook}
                        onChange={(e) => {
                          const newHooks = [...currentTemplate.hook_patterns]
                          newHooks[index] = e.target.value
                          setCurrentTemplate({ ...currentTemplate, hook_patterns: newHooks })
                        }}
                        disabled={!editMode}
                        className="input flex-1"
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Structure Prompts */}
              <div className="card">
                <h3 className="font-bold mb-4">Structure Prompts</h3>
                <div className="space-y-3">
                  {currentTemplate.structure_prompts?.map((prompt, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <input
                        value={prompt}
                        onChange={(e) => {
                          const newPrompts = [...currentTemplate.structure_prompts]
                          newPrompts[index] = e.target.value
                          setCurrentTemplate({ ...currentTemplate, structure_prompts: newPrompts })
                        }}
                        disabled={!editMode}
                        className="input flex-1"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
