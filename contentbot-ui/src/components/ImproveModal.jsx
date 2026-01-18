import { X, Sparkles, Loader } from 'lucide-react'

export default function ImproveModal({
  show,
  onClose,
  onImprove,
  improvementType,
  setImprovementType,
  customInstructions,
  setCustomInstructions,
  loading = false
}) {
  if (!show) return null

  const handleSubmit = (e) => {
    e.preventDefault()
    onImprove()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-card border border-dark-border rounded-lg max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold flex items-center gap-2">
            <Sparkles size={20} className="text-primary-500" />
            Improve Story
          </h3>
          <button
            onClick={onClose}
            disabled={loading}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-300">
              Improvement Instructions
            </label>
            <textarea
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              placeholder="Enter your improvement instructions (e.g., 'Make it scarier', 'Add more humor at the end', 'Improve pacing')"
              className="input w-full h-24 resize-none text-sm"
              disabled={loading}
            />
            <p className="text-xs text-gray-400 mt-1">
              Tell the AI exactly how to improve your story
            </p>
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader size={16} className="animate-spin" />
                  Improving...
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  Improve Story
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
