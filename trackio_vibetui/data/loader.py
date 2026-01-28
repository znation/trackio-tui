"""Async data loader wrapping SQLiteStorage."""

import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from trackio.sqlite_storage import SQLiteStorage

from ..config import TRACKIO_DIR, CACHE_TTL_SECONDS
from .cache import Cache


class TrackioDataLoader:
    """Async wrapper around SQLiteStorage with caching."""

    def __init__(self):
        self._cache = Cache(ttl_seconds=CACHE_TTL_SECONDS)
        self._executor = ThreadPoolExecutor(max_workers=4)

    async def get_projects(self) -> List[str]:
        """Get list of all projects."""
        cache_key = "projects"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        loop = asyncio.get_event_loop()
        projects = await loop.run_in_executor(
            self._executor,
            self._get_projects_sync
        )
        self._cache.set(cache_key, projects)
        return projects

    def _get_projects_sync(self) -> List[str]:
        """Synchronous project list retrieval."""
        if not TRACKIO_DIR.exists():
            return []

        projects = []
        for db_file in TRACKIO_DIR.glob("*.db"):
            # Skip special databases
            if db_file.stem not in ["_global", "_cache"]:
                projects.append(db_file.stem)
        return sorted(projects)

    async def get_runs(self, project: str) -> List[str]:
        """Get list of runs for a project."""
        cache_key = f"runs:{project}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        loop = asyncio.get_event_loop()
        runs = await loop.run_in_executor(
            self._executor,
            SQLiteStorage.get_runs,
            project
        )
        self._cache.set(cache_key, runs)
        return runs

    async def get_all_run_configs(self, project: str) -> Dict[str, Dict[str, Any]]:
        """Get configurations for all runs in a project."""
        cache_key = f"run_configs:{project}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        loop = asyncio.get_event_loop()
        configs = await loop.run_in_executor(
            self._executor,
            SQLiteStorage.get_all_run_configs,
            project
        )
        self._cache.set(cache_key, configs)
        return configs

    async def get_all_metrics_for_run(
        self,
        project: str,
        run_id: str
    ) -> List[str]:
        """Get list of metric names for a run."""
        cache_key = f"metrics:{project}:{run_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        loop = asyncio.get_event_loop()
        metrics = await loop.run_in_executor(
            self._executor,
            SQLiteStorage.get_all_metrics_for_run,
            project,
            run_id
        )
        self._cache.set(cache_key, metrics)
        return metrics

    async def get_metric_values(
        self,
        project: str,
        run_id: str,
        metric_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get metric values for a run.

        Returns list of dicts with keys: step, value, timestamp
        No caching for metric values to ensure fresh data.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            SQLiteStorage.get_metric_values,
            project,
            run_id,
            metric_name
        )

    async def get_system_logs(
        self,
        project: str,
        run_id: str
    ) -> List[Dict[str, Any]]:
        """Get system metrics for a run."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            SQLiteStorage.get_system_logs,
            project,
            run_id
        )

    def invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cache entries."""
        if pattern:
            self._cache.invalidate_pattern(pattern)
        else:
            self._cache.clear()

    def shutdown(self):
        """Shutdown the executor."""
        self._executor.shutdown(wait=False)
