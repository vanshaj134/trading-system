"""
Run Ledger

Maintains an immutable ledger of system runs for Phase 0 memory and accountability.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json


class RunLedger:
    """
    Immutable, append-only ledger of system execution runs.
    
    Records all signal generation, position scaling, optimization, and trade decisions.
    """
    
    def __init__(self, filepath: Optional[str] = None):
        """
        Initialize the run ledger.
        
        Args:
            filepath: Optional path to persist ledger
        """
        self.filepath = filepath
        self.runs: List[Dict[str, Any]] = []
        self.load_if_exists()
    
    def load_if_exists(self):
        """Load ledger from file if it exists."""
        if self.filepath:
            try:
                with open(self.filepath, 'r') as f:
                    self.runs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                self.runs = []
    
    def record_run(self, run_data: Dict[str, Any]) -> str:
        """
        Record a new run (append-only).
        
        Args:
            run_data: Run information
        
        Returns:
            Run ID
        """
        run = {
            'run_id': f"run_{len(self.runs)}_{int(datetime.now().timestamp() * 1000)}",
            'timestamp': datetime.now().isoformat(),
            **run_data
        }
        self.runs.append(run)
        self._persist()
        return run['run_id']
    
    def _persist(self):
        """Persist ledger to file."""
        if self.filepath:
            with open(self.filepath, 'w') as f:
                json.dump(self.runs, f, indent=2)
    
    def get_all_runs(self) -> List[Dict[str, Any]]:
        """Get all recorded runs."""
        return self.runs
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific run by ID."""
        for run in self.runs:
            if run.get('run_id') == run_id:
                return run
        return None
    
    def get_latest_run(self) -> Optional[Dict[str, Any]]:
        """Get the most recent run."""
        return self.runs[-1] if self.runs else None
    
    def get_run_count(self) -> int:
        """Get total number of runs."""
        return len(self.runs)
