import { AlertCircle, RefreshCw, X } from 'lucide-react'

export default function RecoveryNotification({ onResume, onDismiss, state }) {
  const getStepName = (step) => {
    switch (step) {
      case 1: return 'Story generation'
      case 2: return 'Audio generation'
      case 3: return 'Subtitle generation'
      case 4: return 'Video rendering'
      case 5: return 'Video complete'
      default: return 'Unknown step'
    }
  }

  const getRecoveryMessage = () => {
    if (state.videoData) {
      return 'Your video is ready! Click to view it.'
    }
    if (state.step >= 1) {
      return `You were working on ${getStepName(state.step)}. Continue where you left off?`
    }
    return 'Resume your previous session?'
  }

  return (
    <div className="fixed top-4 right-4 z-50 max-w-md">
      <div className="card bg-primary-900 bg-opacity-90 border-primary-600 shadow-lg">
        <div className="flex items-start gap-3">
          <AlertCircle size={24} className="text-primary-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-white mb-1">Session Recovery</h3>
            <p className="text-sm text-gray-300 mb-3">
              {getRecoveryMessage()}
            </p>
            {state.step > 0 && (
              <div className="text-xs text-gray-400 mb-3 space-y-1">
                <p>• Current step: <span className="text-white">{getStepName(state.step)}</span></p>
                {state.storyData && <p>• Story: <span className="text-white">{state.storyData.word_count} words</span></p>}
                {state.audioData && <p>• Audio: <span className="text-white">{state.audioData.duration?.toFixed(1)}s</span></p>}
                {state.selectedGenre && <p>• Genre: <span className="text-white capitalize">{state.selectedGenre}</span></p>}
              </div>
            )}
            <div className="flex gap-2">
              <button
                onClick={onResume}
                className="btn-primary text-sm py-2 px-3 flex items-center gap-2"
              >
                <RefreshCw size={14} />
                Resume
              </button>
              <button
                onClick={onDismiss}
                className="btn-secondary text-sm py-2 px-3 flex items-center gap-2"
              >
                <X size={14} />
                Start Fresh
              </button>
            </div>
          </div>
          <button
            onClick={onDismiss}
            className="text-gray-400 hover:text-white transition-colors flex-shrink-0"
          >
            <X size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
