import { PenLine, Sparkles, Wand2 } from 'lucide-react'

export default function StoryModeSelector({ mode, onModeChange, disabled = false }) {
  const modes = [
    {
      id: 'generate',
      label: 'Generate',
      icon: Sparkles,
      desc: 'AI creates story from scratch'
    },
    {
      id: 'write',
      label: 'Write',
      icon: PenLine,
      desc: 'Write your own story manually'
    },
    {
      id: 'improve',
      label: 'Improve',
      icon: Wand2,
      desc: 'Enhance existing story with AI'
    }
  ]

  return (
    <div className="mb-6">
      <div className="flex gap-2 border-b border-dark-border flex-wrap">
        {modes.map(({ id, label, icon: Icon, desc }) => (
          <button
            key={id}
            onClick={() => onModeChange(id)}
            disabled={disabled}
            className={`px-4 py-3 font-medium transition-colors flex items-center gap-2 ${
              mode === id
                ? 'border-b-2 border-primary-500 text-white'
                : 'text-gray-400 hover:text-gray-300 border-b-2 border-transparent'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <Icon size={18} />
            <span>{label}</span>
          </button>
        ))}
      </div>

      <div className="mt-3">
        <p className="text-sm text-gray-400">
          {modes.find(m => m.id === mode)?.desc}
        </p>
      </div>
    </div>
  )
}
