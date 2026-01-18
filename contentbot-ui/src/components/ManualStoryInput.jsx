import { ArrowRight } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function ManualStoryInput({ value, onChange, onContinue, loading = false }) {
  const [wordCount, setWordCount] = useState(0)
  const [duration, setDuration] = useState(0)

  useEffect(() => {
    const words = value.trim().split(/\s+/).filter(w => w.length > 0).length
    setWordCount(words)
    setDuration(Math.ceil(words / 2.5))
  }, [value])

  const handleContinue = () => {
    if (value.trim().length === 0) {
      return
    }
    onContinue()
  }

  const isValid = wordCount >= 50
  const isOptimal = wordCount >= 100

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2 text-gray-300">
          Write Your Story
        </label>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Start typing your story here...&#10;&#10;Tips:&#10;• Aim for 100+ words (60+ seconds) for monetization&#10;• Use short sentences and natural language&#10;• Create a strong hook in the first line&#10;• Build emotional tension or humor"
          className="input w-full h-48 md:h-64 resize-none font-mono text-sm"
          disabled={loading}
        />
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-400">
          <span className={wordCount >= 100 ? 'text-green-400 font-medium' : wordCount >= 50 ? 'text-yellow-400' : 'text-gray-400'}>
            {wordCount} words
          </span>
          <span className="mx-2">•</span>
          <span className={duration >= 60 ? 'text-green-400 font-medium' : 'text-gray-400'}>
            ~{duration}s duration
          </span>
          {!isOptimal && wordCount > 0 && (
            <>
              <span className="mx-2">•</span>
              <span className="text-yellow-400">
                {isValid ? 'Consider adding more detail' : 'Too short (minimum 50 words)'}
              </span>
            </>
          )}
          {isOptimal && (
            <>
              <span className="mx-2">•</span>
              <span className="text-green-400">
                ✓ Good length for monetization
              </span>
            </>
          )}
        </div>

        <button
          onClick={handleContinue}
          disabled={loading || !isValid}
          className={`btn-primary flex items-center gap-2 ${!isValid ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          Continue to Audio
          <ArrowRight size={16} />
        </button>
      </div>
    </div>
  )
}
