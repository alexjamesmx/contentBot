"""Job tracking system for generation tasks.

Scalable architecture:
- Current: In-memory dict (development)
- Future: Redis/DynamoDB (production)
- Interface remains identical for easy migration
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from src.utils.config import PROJECT_ROOT


class JobStatus:
    """Job status constants"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType:
    """Job type constants"""
    STORY = "story"
    AUDIO = "audio"
    SUBTITLES = "subtitles"
    VIDEO = "video"
    BATCH = "batch"


class Job:
    """Job data structure"""
    def __init__(
        self,
        job_id: str,
        job_type: str,
        status: str = JobStatus.PENDING,
        progress: float = 0.0,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.job_id = job_id
        self.job_type = job_type
        self.status = status
        self.progress = progress
        self.result = result or {}
        self.error = error
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.updated_at = time.time()

    def to_dict(self) -> dict:
        """Serialize to dict"""
        return {
            'job_id': self.job_id,
            'job_type': self.job_type,
            'status': self.status,
            'progress': self.progress,
            'result': self.result,
            'error': self.error,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data: dict) -> 'Job':
        """Deserialize from dict"""
        job = Job(
            job_id=data['job_id'],
            job_type=data['job_type'],
            status=data['status'],
            progress=data.get('progress', 0.0),
            result=data.get('result'),
            error=data.get('error'),
            metadata=data.get('metadata')
        )
        job.created_at = data.get('created_at', time.time())
        job.updated_at = data.get('updated_at', time.time())
        return job


class JobTrackerInterface(ABC):
    """Abstract interface for job tracking.

    Allows swapping backends:
    - Local development: InMemoryJobTracker
    - Production: RedisJobTracker, DynamoDBJobTracker, etc.
    """

    @abstractmethod
    def create_job(self, job_id: str, job_type: str, metadata: Optional[Dict] = None) -> Job:
        """Create a new job"""
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        pass

    @abstractmethod
    def update_job(self, job_id: str, **updates) -> Optional[Job]:
        """Update job fields"""
        pass

    @abstractmethod
    def delete_job(self, job_id: str) -> bool:
        """Delete job"""
        pass

    @abstractmethod
    def list_active_jobs(self) -> List[Job]:
        """List all active (pending/running) jobs"""
        pass

    @abstractmethod
    def list_user_jobs(self, limit: int = 50) -> List[Job]:
        """List recent jobs for user"""
        pass

    @abstractmethod
    def cleanup_old_jobs(self, max_age_seconds: int = 86400) -> int:
        """Clean up old completed jobs"""
        pass


class InMemoryJobTracker(JobTrackerInterface):
    """In-memory job tracker (current implementation).

    Stores jobs in memory dict. Jobs lost on server restart.
    Good for: Development, testing
    """

    def __init__(self):
        self.jobs: Dict[str, Job] = {}

    def create_job(self, job_id: str, job_type: str, metadata: Optional[Dict] = None) -> Job:
        job = Job(job_id=job_id, job_type=job_type, metadata=metadata)
        self.jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    def update_job(self, job_id: str, **updates) -> Optional[Job]:
        job = self.jobs.get(job_id)
        if not job:
            return None

        for key, value in updates.items():
            if hasattr(job, key):
                setattr(job, key, value)

        job.updated_at = time.time()
        return job

    def delete_job(self, job_id: str) -> bool:
        if job_id in self.jobs:
            del self.jobs[job_id]
            return True
        return False

    def list_active_jobs(self) -> List[Job]:
        return [
            job for job in self.jobs.values()
            if job.status in [JobStatus.PENDING, JobStatus.RUNNING]
        ]

    def list_user_jobs(self, limit: int = 50) -> List[Job]:
        jobs = sorted(
            self.jobs.values(),
            key=lambda j: j.updated_at,
            reverse=True
        )
        return jobs[:limit]

    def cleanup_old_jobs(self, max_age_seconds: int = 86400) -> int:
        """Remove completed jobs older than max_age_seconds"""
        cutoff = time.time() - max_age_seconds
        to_delete = [
            job_id for job_id, job in self.jobs.items()
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
            and job.updated_at < cutoff
        ]

        for job_id in to_delete:
            del self.jobs[job_id]

        return len(to_delete)


class FileBasedJobTracker(JobTrackerInterface):
    """File-based job tracker (persistence across restarts).

    Stores jobs in JSON files. Survives server restarts.
    Good for: Single-server production, development
    Migration path: Easy to sync files to S3
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or (PROJECT_ROOT / "output" / "jobs")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_job_path(self, job_id: str) -> Path:
        return self.storage_dir / f"{job_id}.json"

    def create_job(self, job_id: str, job_type: str, metadata: Optional[Dict] = None) -> Job:
        job = Job(job_id=job_id, job_type=job_type, metadata=metadata)
        self._save_job(job)
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        job_path = self._get_job_path(job_id)
        if not job_path.exists():
            return None

        try:
            with open(job_path, 'r') as f:
                data = json.load(f)
            return Job.from_dict(data)
        except Exception as e:
            print(f"Error loading job {job_id}: {e}")
            return None

    def update_job(self, job_id: str, **updates) -> Optional[Job]:
        job = self.get_job(job_id)
        if not job:
            return None

        for key, value in updates.items():
            if hasattr(job, key):
                setattr(job, key, value)

        job.updated_at = time.time()
        self._save_job(job)
        return job

    def delete_job(self, job_id: str) -> bool:
        job_path = self._get_job_path(job_id)
        if job_path.exists():
            job_path.unlink()
            return True
        return False

    def list_active_jobs(self) -> List[Job]:
        jobs = []
        for job_file in self.storage_dir.glob("*.json"):
            job = self.get_job(job_file.stem)
            if job and job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
                jobs.append(job)
        return jobs

    def list_user_jobs(self, limit: int = 50) -> List[Job]:
        jobs = []
        for job_file in self.storage_dir.glob("*.json"):
            job = self.get_job(job_file.stem)
            if job:
                jobs.append(job)

        jobs.sort(key=lambda j: j.updated_at, reverse=True)
        return jobs[:limit]

    def cleanup_old_jobs(self, max_age_seconds: int = 86400) -> int:
        cutoff = time.time() - max_age_seconds
        deleted = 0

        for job_file in self.storage_dir.glob("*.json"):
            job = self.get_job(job_file.stem)
            if job and job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                if job.updated_at < cutoff:
                    self.delete_job(job.job_id)
                    deleted += 1

        return deleted

    def _save_job(self, job: Job):
        """Save job to file"""
        job_path = self._get_job_path(job.job_id)
        with open(job_path, 'w') as f:
            json.dump(job.to_dict(), f, indent=2)


# Global job tracker instance
# Can be swapped: _job_tracker = RedisJobTracker() for production
_job_tracker: JobTrackerInterface = FileBasedJobTracker()


def get_job_tracker() -> JobTrackerInterface:
    """Get the global job tracker instance.

    Factory pattern allows easy swapping:
    - Development: FileBasedJobTracker
    - Production: RedisJobTracker, DynamoDBJobTracker
    """
    return _job_tracker


def set_job_tracker(tracker: JobTrackerInterface):
    """Set custom job tracker (for testing or production)"""
    global _job_tracker
    _job_tracker = tracker


# Convenience functions
def create_job(job_id: str, job_type: str, metadata: Optional[Dict] = None) -> Job:
    return get_job_tracker().create_job(job_id, job_type, metadata)


def get_job(job_id: str) -> Optional[Job]:
    return get_job_tracker().get_job(job_id)


def update_job(job_id: str, **updates) -> Optional[Job]:
    return get_job_tracker().update_job(job_id, **updates)


def delete_job(job_id: str) -> bool:
    return get_job_tracker().delete_job(job_id)


def list_active_jobs() -> List[Job]:
    return get_job_tracker().list_active_jobs()


def list_user_jobs(limit: int = 50) -> List[Job]:
    return get_job_tracker().list_user_jobs(limit)
