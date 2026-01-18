import { useState } from 'react'
import { Edit2, Trash2, Plus, Zap, Type, Film, Check, X } from 'lucide-react'

export default function EffectInspector({
  effectTimeline,
  onUpdateEffect,
  onDeleteEffect,
  onAddEffect,
  audioDuration = 60,
  disabled = false
}) {
  const [editingId, setEditingId] = useState(null)
  const [showAddMenu, setShowAddMenu] = useState(false)
  const [editForm, setEditForm] = useState({})

  const startEdit = (effect) => {
    setEditingId(effect.id)
    setEditForm({
      ...effect.trigger,
      ...effect.parameters,
      type: effect.type
    })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditForm({})
  }

  const saveEdit = (effectId) => {
    const effect = effectTimeline.find(e => e.id === effectId)
    if (!effect) return

    const updatedEffect = { ...effect }

    if (effect.type === 'zoom_effect') {
      updatedEffect.parameters = {
        scale: parseFloat(editForm.scale) || 1.2,
        duration_ms: parseInt(editForm.duration_ms) || 300
      }
      if (editForm.triggerType === 'time') {
        updatedEffect.trigger = {
          type: 'time',
          time: parseFloat(editForm.time) || 0
        }
      } else {
        updatedEffect.trigger = {
          type: 'word_match',
          pattern: editForm.pattern || ''
        }
      }
    } else if (effect.type === 'subtitle_style_override') {
      updatedEffect.parameters = {
        color: editForm.color || 'yellow',
        size: parseInt(editForm.size) || 72
      }
      updatedEffect.trigger = {
        type: 'time_range',
        start_time: parseFloat(editForm.start_time) || 0,
        end_time: parseFloat(editForm.end_time) || audioDuration
      }
    } else if (effect.type === 'background_change') {
      updatedEffect.parameters = {
        new_source: editForm.new_source || '',
        transition: editForm.transition || 'cut',
        transition_duration: parseFloat(editForm.transition_duration) || 1.0
      }
      updatedEffect.trigger = {
        type: 'time',
        time: parseFloat(editForm.time) || 0
      }
    }

    onUpdateEffect(effectId, updatedEffect)
    setEditingId(null)
    setEditForm({})
  }

  const renderEffectCard = (effect) => {
    const isEditing = editingId === effect.id

    if (effect.type === 'zoom_effect') {
      const trigger = effect.trigger
      const params = effect.parameters

      return (
        <div key={effect.id} className="bg-dark-hover p-4 rounded border border-purple-700">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <Zap size={18} className="text-purple-400" />
              <span className="font-medium text-purple-300">Zoom Effect</span>
              <span className="text-xs text-gray-500">({effect.id})</span>
            </div>
            {!isEditing && (
              <div className="flex gap-2">
                <button
                  onClick={() => startEdit(effect)}
                  className="text-gray-400 hover:text-white p-1"
                  disabled={disabled}
                >
                  <Edit2 size={14} />
                </button>
                <button
                  onClick={() => onDeleteEffect(effect.id)}
                  className="text-red-400 hover:text-red-300 p-1"
                  disabled={disabled}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )}
          </div>

          {isEditing ? (
            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-400 block mb-1">Trigger Type</label>
                <select
                  value={editForm.triggerType || trigger.type}
                  onChange={(e) => setEditForm({ ...editForm, triggerType: e.target.value })}
                  className="input w-full text-sm"
                >
                  <option value="word_match">Word Match</option>
                  <option value="time">Specific Time</option>
                </select>
              </div>

              {(editForm.triggerType || trigger.type) === 'word_match' ? (
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Word Pattern (regex)</label>
                  <input
                    type="text"
                    value={editForm.pattern !== undefined ? editForm.pattern : trigger.pattern}
                    onChange={(e) => setEditForm({ ...editForm, pattern: e.target.value })}
                    placeholder="bro|literally|insane"
                    className="input w-full text-sm"
                  />
                  <p className="text-xs text-gray-500 mt-1">Use | to separate words</p>
                </div>
              ) : (
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Time (seconds)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={editForm.time !== undefined ? editForm.time : trigger.time}
                    onChange={(e) => setEditForm({ ...editForm, time: e.target.value })}
                    className="input w-full text-sm"
                  />
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Scale</label>
                  <input
                    type="number"
                    step="0.05"
                    min="1.0"
                    max="2.0"
                    value={editForm.scale !== undefined ? editForm.scale : params.scale}
                    onChange={(e) => setEditForm({ ...editForm, scale: e.target.value })}
                    className="input w-full text-sm"
                  />
                  <p className="text-xs text-gray-500 mt-1">1.1-1.2 subtle, 1.3-1.5 dramatic</p>
                </div>
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Duration (ms)</label>
                  <input
                    type="number"
                    step="50"
                    min="100"
                    max="1000"
                    value={editForm.duration_ms !== undefined ? editForm.duration_ms : params.duration_ms}
                    onChange={(e) => setEditForm({ ...editForm, duration_ms: e.target.value })}
                    className="input w-full text-sm"
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <button onClick={() => saveEdit(effect.id)} className="btn-primary text-sm flex items-center gap-1">
                  <Check size={14} /> Save
                </button>
                <button onClick={cancelEdit} className="btn-secondary text-sm flex items-center gap-1">
                  <X size={14} /> Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="text-sm space-y-1">
              {trigger.type === 'word_match' ? (
                <p className="text-gray-300">
                  <span className="text-gray-500">Trigger:</span> Words matching "{trigger.pattern}"
                </p>
              ) : (
                <p className="text-gray-300">
                  <span className="text-gray-500">Trigger:</span> At {trigger.time}s
                </p>
              )}
              <p className="text-gray-300">
                <span className="text-gray-500">Scale:</span> {params.scale}x
                <span className="ml-4 text-gray-500">Duration:</span> {params.duration_ms}ms
              </p>
            </div>
          )}
        </div>
      )
    }

    if (effect.type === 'subtitle_style_override') {
      const trigger = effect.trigger
      const params = effect.parameters

      return (
        <div key={effect.id} className="bg-dark-hover p-4 rounded border border-purple-700">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <Type size={18} className="text-purple-400" />
              <span className="font-medium text-purple-300">Subtitle Style</span>
              <span className="text-xs text-gray-500">({effect.id})</span>
            </div>
            {!isEditing && (
              <div className="flex gap-2">
                <button
                  onClick={() => startEdit(effect)}
                  className="text-gray-400 hover:text-white p-1"
                  disabled={disabled}
                >
                  <Edit2 size={14} />
                </button>
                <button
                  onClick={() => onDeleteEffect(effect.id)}
                  className="text-red-400 hover:text-red-300 p-1"
                  disabled={disabled}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )}
          </div>

          {isEditing ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Start Time (s)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={editForm.start_time !== undefined ? editForm.start_time : trigger.start_time}
                    onChange={(e) => setEditForm({ ...editForm, start_time: e.target.value })}
                    className="input w-full text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-400 block mb-1">End Time (s)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={editForm.end_time !== undefined ? editForm.end_time : trigger.end_time}
                    onChange={(e) => setEditForm({ ...editForm, end_time: e.target.value })}
                    className="input w-full text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Color</label>
                  <select
                    value={editForm.color !== undefined ? editForm.color : params.color}
                    onChange={(e) => setEditForm({ ...editForm, color: e.target.value })}
                    className="input w-full text-sm"
                  >
                    <option value="yellow">Yellow (Default)</option>
                    <option value="white">White</option>
                    <option value="red">Red</option>
                    <option value="green">Green</option>
                    <option value="blue">Blue</option>
                    <option value="cyan">Cyan</option>
                    <option value="magenta">Magenta</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Font Size (px)</label>
                  <input
                    type="number"
                    step="2"
                    min="40"
                    max="120"
                    value={editForm.size !== undefined ? editForm.size : params.size}
                    onChange={(e) => setEditForm({ ...editForm, size: e.target.value })}
                    className="input w-full text-sm"
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <button onClick={() => saveEdit(effect.id)} className="btn-primary text-sm flex items-center gap-1">
                  <Check size={14} /> Save
                </button>
                <button onClick={cancelEdit} className="btn-secondary text-sm flex items-center gap-1">
                  <X size={14} /> Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="text-sm space-y-1">
              <p className="text-gray-300">
                <span className="text-gray-500">Time Range:</span> {trigger.start_time}s - {trigger.end_time}s
              </p>
              <p className="text-gray-300">
                <span className="text-gray-500">Color:</span>
                <span style={{ color: params.color }} className="ml-1 font-bold">{params.color}</span>
                <span className="ml-4 text-gray-500">Size:</span> {params.size}px
              </p>
            </div>
          )}
        </div>
      )
    }

    if (effect.type === 'background_change') {
      const trigger = effect.trigger
      const params = effect.parameters

      return (
        <div key={effect.id} className="bg-dark-hover p-4 rounded border border-purple-700">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <Film size={18} className="text-purple-400" />
              <span className="font-medium text-purple-300">Background Change</span>
              <span className="text-xs text-gray-500">({effect.id})</span>
            </div>
            {!isEditing && (
              <div className="flex gap-2">
                <button
                  onClick={() => startEdit(effect)}
                  className="text-gray-400 hover:text-white p-1"
                  disabled={disabled}
                >
                  <Edit2 size={14} />
                </button>
                <button
                  onClick={() => onDeleteEffect(effect.id)}
                  className="text-red-400 hover:text-red-300 p-1"
                  disabled={disabled}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )}
          </div>

          {isEditing ? (
            <div className="space-y-3">
              <div>
                <label className="text-xs text-gray-400 block mb-1">Switch Time (s)</label>
                <input
                  type="number"
                  step="0.1"
                  value={editForm.time !== undefined ? editForm.time : trigger.time}
                  onChange={(e) => setEditForm({ ...editForm, time: e.target.value })}
                  className="input w-full text-sm"
                />
              </div>

              <div>
                <label className="text-xs text-gray-400 block mb-1">New Background (filename)</label>
                <input
                  type="text"
                  value={editForm.new_source !== undefined ? editForm.new_source : params.new_source}
                  onChange={(e) => setEditForm({ ...editForm, new_source: e.target.value })}
                  placeholder="minecraft_2.mp4"
                  className="input w-full text-sm"
                />
                <p className="text-xs text-gray-500 mt-1">Filename from assets/backgrounds/</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Transition</label>
                  <select
                    value={editForm.transition !== undefined ? editForm.transition : params.transition}
                    onChange={(e) => setEditForm({ ...editForm, transition: e.target.value })}
                    className="input w-full text-sm"
                  >
                    <option value="cut">Cut (Instant)</option>
                    <option value="fade">Fade (Smooth)</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-400 block mb-1">Fade Duration (s)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    max="3.0"
                    value={editForm.transition_duration !== undefined ? editForm.transition_duration : params.transition_duration}
                    onChange={(e) => setEditForm({ ...editForm, transition_duration: e.target.value })}
                    className="input w-full text-sm"
                    disabled={editForm.transition === 'cut'}
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <button onClick={() => saveEdit(effect.id)} className="btn-primary text-sm flex items-center gap-1">
                  <Check size={14} /> Save
                </button>
                <button onClick={cancelEdit} className="btn-secondary text-sm flex items-center gap-1">
                  <X size={14} /> Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="text-sm space-y-1">
              <p className="text-gray-300">
                <span className="text-gray-500">Switch at:</span> {trigger.time}s
              </p>
              <p className="text-gray-300">
                <span className="text-gray-500">New Source:</span> {params.new_source}
              </p>
              <p className="text-gray-300">
                <span className="text-gray-500">Transition:</span> {params.transition}
                {params.transition === 'fade' && <span className="ml-2">({params.transition_duration}s)</span>}
              </p>
            </div>
          )}
        </div>
      )
    }

    return null
  }

  const addManualEffect = (type) => {
    let newEffect = {}

    if (type === 'zoom_time') {
      newEffect = {
        id: `zoom_${Date.now()}`,
        type: 'zoom_effect',
        trigger: { type: 'time', time: 5.0 },
        parameters: { scale: 1.2, duration_ms: 300 }
      }
    } else if (type === 'zoom_word') {
      newEffect = {
        id: `zoom_${Date.now()}`,
        type: 'zoom_effect',
        trigger: { type: 'word_match', pattern: 'bro' },
        parameters: { scale: 1.15, duration_ms: 300 }
      }
    } else if (type === 'subtitle_style') {
      newEffect = {
        id: `subtitle_${Date.now()}`,
        type: 'subtitle_style_override',
        trigger: { type: 'time_range', start_time: 50.0, end_time: 60.0 },
        parameters: { color: 'red', size: 84 }
      }
    } else if (type === 'background') {
      newEffect = {
        id: `background_${Date.now()}`,
        type: 'background_change',
        trigger: { type: 'time', time: 30.0 },
        parameters: { new_source: 'minecraft_2.mp4', transition: 'cut', transition_duration: 1.0 }
      }
    }

    onAddEffect(newEffect)
    setShowAddMenu(false)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-purple-300">
          Effect Timeline ({effectTimeline.length} effect{effectTimeline.length !== 1 ? 's' : ''})
        </h4>
        <button
          onClick={() => setShowAddMenu(!showAddMenu)}
          className="btn-secondary text-xs flex items-center gap-1"
          disabled={disabled}
        >
          <Plus size={14} /> Add Effect
        </button>
      </div>

      {showAddMenu && (
        <div className="mb-3 p-3 bg-dark-card rounded border border-purple-700">
          <p className="text-xs text-gray-400 mb-2">Choose effect type to add:</p>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => addManualEffect('zoom_time')}
              className="btn-secondary text-xs flex items-center gap-1 justify-start"
            >
              <Zap size={12} /> Zoom at Time
            </button>
            <button
              onClick={() => addManualEffect('zoom_word')}
              className="btn-secondary text-xs flex items-center gap-1 justify-start"
            >
              <Zap size={12} /> Zoom on Word
            </button>
            <button
              onClick={() => addManualEffect('subtitle_style')}
              className="btn-secondary text-xs flex items-center gap-1 justify-start"
            >
              <Type size={12} /> Subtitle Style
            </button>
            <button
              onClick={() => addManualEffect('background')}
              className="btn-secondary text-xs flex items-center gap-1 justify-start"
            >
              <Film size={12} /> Background Change
            </button>
          </div>
        </div>
      )}

      {effectTimeline.length === 0 ? (
        <div className="text-center py-8 text-gray-500 text-sm">
          <p>No effects added yet</p>
          <p className="text-xs mt-1">Use AI prompt above or click "Add Effect"</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {effectTimeline.map(effect => renderEffectCard(effect))}
        </div>
      )}
    </div>
  )
}
