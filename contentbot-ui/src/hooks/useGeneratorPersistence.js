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

const STORAGE_KEY_PREFIX = 'contentbot_generator_state'
const AUTO_SAVE_DELAY = 1000 // Debounce saves (1 second)

export function useGeneratorPersistence(state, setState) {
  const saveTimerRef = useRef(null)
  const isRestoringRef = useRef(false)

  // Generate unique key per series part
  const getStorageKey = () => {
    if (state.seriesId && state.currentPartNumber) {
      return `${STORAGE_KEY_PREFIX}_series_${state.seriesId}_part_${state.currentPartNumber}`
    }
    return STORAGE_KEY_PREFIX
  }

  // Restore state on mount
  useEffect(() => {
    const savedState = loadState(getStorageKey())
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
      saveState(state, getStorageKey())
    }, AUTO_SAVE_DELAY)

    return () => {
      if (saveTimerRef.current) {
        clearTimeout(saveTimerRef.current)
      }
    }
  }, [state])

  return {
    clearSavedState: () => clearState(getStorageKey()),
    hasSavedState: () => hasSavedState(getStorageKey())
  }
}

function saveState(state, storageKey) {
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

    // Save series state (if in series mode)
    if (state.seriesId) stateToSave.seriesId = state.seriesId
    if (state.currentPartNumber) stateToSave.currentPartNumber = state.currentPartNumber
    if (state.seriesMode !== undefined) stateToSave.seriesMode = state.seriesMode
    if (state.seriesTheme) stateToSave.seriesTheme = state.seriesTheme
    if (state.totalParts) stateToSave.totalParts = state.totalParts

    // Add metadata
    stateToSave._timestamp = Date.now()
    stateToSave._version = '1.0'

    localStorage.setItem(storageKey, JSON.stringify(stateToSave))
  } catch (error) {
    console.error('Failed to save generator state:', error)
  }
}

function loadState(storageKey) {
  try {
    const saved = localStorage.getItem(storageKey)
    if (!saved) return null

    const state = JSON.parse(saved)

    // Check if state is too old (>24 hours)
    if (state._timestamp && (Date.now() - state._timestamp) > 24 * 60 * 60 * 1000) {
      console.log('Saved state expired, clearing...')
      clearState(storageKey)
      return null
    }

    return state
  } catch (error) {
    console.error('Failed to load generator state:', error)
    return null
  }
}

function clearState(storageKey) {
  try {
    localStorage.removeItem(storageKey)
  } catch (error) {
    console.error('Failed to clear generator state:', error)
  }
}

function hasSavedState(storageKey) {
  try {
    const saved = localStorage.getItem(storageKey)
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
