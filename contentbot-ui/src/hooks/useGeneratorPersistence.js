/**
 * Generator State Persistence Hook
 *
 * Saves and restores Generator state to/from localStorage.
 * Enables recovery after:
 * - Tab switches
 * - Page refreshes
 * - Browser crashes
 *
 * Architecture:
 * - Current: localStorage (browser-based)
 * - Future: Could sync to cloud (S3, backend API)
 */

import { useEffect, useRef } from 'react'

const STORAGE_KEY = 'contentbot_generator_state'
const AUTO_SAVE_DELAY = 1000 // Debounce saves (1 second)

export function useGeneratorPersistence(state, setState) {
  const saveTimerRef = useRef(null)
  const isRestoringRef = useRef(false)

  // Restore state on mount
  useEffect(() => {
    const savedState = loadState()
    if (savedState && Object.keys(savedState).length > 0) {
      isRestoringRef.current = true
      setState(savedState)
      setTimeout(() => {
        isRestoringRef.current = false
      }, 100)
    }
  }, [])

  // Auto-save state changes (debounced)
  useEffect(() => {
    // Don't save during initial restore
    if (isRestoringRef.current) return

    // Clear previous timer
    if (saveTimerRef.current) {
      clearTimeout(saveTimerRef.current)
    }

    // Debounce save
    saveTimerRef.current = setTimeout(() => {
      saveState(state)
    }, AUTO_SAVE_DELAY)

    return () => {
      if (saveTimerRef.current) {
        clearTimeout(saveTimerRef.current)
      }
    }
  }, [state])

  return {
    clearSavedState: () => clearState(),
    hasSavedState: () => hasSavedState()
  }
}

function saveState(state) {
  try {
    // Filter out empty/default state to save space
    const stateToSave = {}

    if (state.step > 0) stateToSave.step = state.step
    if (state.storyData) stateToSave.storyData = state.storyData
    if (state.audioData) stateToSave.audioData = state.audioData
    if (state.subtitleData) stateToSave.subtitleData = state.subtitleData
    if (state.videoData) stateToSave.videoData = state.videoData
    if (state.editStory) stateToSave.editStory = state.editStory
    if (state.editSubtitles && state.editSubtitles.length > 0) {
      stateToSave.editSubtitles = state.editSubtitles
    }

    // Save settings
    stateToSave.selectedGenre = state.selectedGenre
    stateToSave.selectedBackground = state.selectedBackground
    stateToSave.selectedVoice = state.selectedVoice
    stateToSave.wordsPerChunk = state.wordsPerChunk
    stateToSave.targetDuration = state.targetDuration
    stateToSave.useElevenLabs = state.useElevenLabs

    // Add metadata
    stateToSave._timestamp = Date.now()
    stateToSave._version = '1.0'

    localStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave))
  } catch (error) {
    console.error('Failed to save generator state:', error)
  }
}

function loadState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) return null

    const state = JSON.parse(saved)

    // Check if state is too old (>24 hours)
    if (state._timestamp && (Date.now() - state._timestamp) > 24 * 60 * 60 * 1000) {
      console.log('Saved state expired, clearing...')
      clearState()
      return null
    }

    return state
  } catch (error) {
    console.error('Failed to load generator state:', error)
    return null
  }
}

function clearState() {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (error) {
    console.error('Failed to clear generator state:', error)
  }
}

function hasSavedState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved !== null && saved !== undefined && saved !== ''
  } catch (error) {
    return false
  }
}

// Job tracking helpers (polls backend for active jobs)
export async function checkActiveJobs(apiUrl) {
  try {
    const response = await fetch(`${apiUrl}/jobs/active`)
    const data = await response.json()

    if (data.success && data.jobs && data.jobs.length > 0) {
      return data.jobs
    }
    return []
  } catch (error) {
    console.error('Failed to check active jobs:', error)
    return []
  }
}

export async function getJobStatus(apiUrl, jobId) {
  try {
    const response = await fetch(`${apiUrl}/jobs/${jobId}`)
    const data = await response.json()

    if (data.success && data.job) {
      return data.job
    }
    return null
  } catch (error) {
    console.error(`Failed to get job ${jobId} status:`, error)
    return null
  }
}

/**
 * Progress polling hook
 * Polls backend for job updates at regular intervals
 */
export function useJobProgressPolling(jobId, apiUrl, onUpdate, interval = 2000) {
  const { useEffect, useRef } = require('react')

  useEffect(() => {
    if (!jobId) return

    const pollInterval = setInterval(async () => {
      const job = await getJobStatus(apiUrl, jobId)
      if (job) {
        onUpdate(job)

        // Stop polling when job is complete or failed
        if (job.status === 'completed' || job.status === 'failed' || job.status === 'cancelled') {
          clearInterval(pollInterval)
        }
      }
    }, interval)

    return () => clearInterval(pollInterval)
  }, [jobId, apiUrl, interval])
}

/**
 * Poll for multiple active jobs
 * Returns current status of all jobs
 */
export async function pollActiveJobs(apiUrl, onJobUpdate) {
  try {
    const jobs = await checkActiveJobs(apiUrl)

    for (const job of jobs) {
      onJobUpdate(job)
    }

    return jobs
  } catch (error) {
    console.error('Failed to poll active jobs:', error)
    return []
  }
}
