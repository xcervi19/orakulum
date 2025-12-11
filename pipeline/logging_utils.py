"""
Logging utilities for the pipeline.
Provides structured JSONL logging and console output.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class PipelineLogger:
    """
    Structured logger for pipeline runs.
    Logs to both console and JSONL files.
    """
    
    def __init__(self, run_dir: Path, client_id: str):
        """
        Initialize logger for a specific run.
        
        Args:
            run_dir: Directory for this run's artifacts
            client_id: The client being processed
        """
        self.run_dir = run_dir
        self.client_id = client_id
        self.logs_dir = run_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Main log file
        self.log_file = self.logs_dir / "pipeline.jsonl"
        
        # Run summary
        self.summary = {
            "client_id": client_id,
            "run_dir": str(run_dir),
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "running",
            "steps": [],
            "errors": [],
        }
    
    def _write_log(self, entry: Dict[str, Any]) -> None:
        """Write a log entry to the JSONL file."""
        entry["timestamp"] = datetime.utcnow().isoformat()
        entry["client_id"] = self.client_id
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def log_step_start(self, step_name: str, details: Optional[Dict] = None) -> None:
        """Log the start of a pipeline step."""
        entry = {
            "event": "step_start",
            "step": step_name,
            "details": details or {},
        }
        self._write_log(entry)
        print(f"🚀 [{self.client_id}] Starting: {step_name}")
    
    def log_step_complete(self, step_name: str, duration_ms: int = 0, 
                          output_path: Optional[str] = None) -> None:
        """Log successful completion of a step."""
        entry = {
            "event": "step_complete",
            "step": step_name,
            "duration_ms": duration_ms,
            "output_path": output_path,
        }
        self._write_log(entry)
        
        self.summary["steps"].append({
            "name": step_name,
            "status": "completed",
            "duration_ms": duration_ms,
        })
        
        print(f"✅ [{self.client_id}] Completed: {step_name} ({duration_ms}ms)")
    
    def log_step_error(self, step_name: str, error: Exception, 
                       retry_count: int = 0) -> None:
        """Log an error during a step."""
        error_msg = f"{type(error).__name__}: {str(error)}"
        
        entry = {
            "event": "step_error",
            "step": step_name,
            "error": error_msg,
            "retry_count": retry_count,
        }
        self._write_log(entry)
        
        self.summary["errors"].append({
            "step": step_name,
            "error": error_msg,
            "retry_count": retry_count,
        })
        
        print(f"❌ [{self.client_id}] Error in {step_name}: {error_msg}")
    
    def log_prompt_execution(self, prompt_name: str, prompt_path: str,
                             response_path: str, success: bool,
                             duration_ms: int = 0) -> None:
        """Log a ChatGPT prompt execution."""
        entry = {
            "event": "prompt_execution",
            "prompt_name": prompt_name,
            "prompt_path": prompt_path,
            "response_path": response_path,
            "success": success,
            "duration_ms": duration_ms,
        }
        self._write_log(entry)
        
        status = "✅" if success else "❌"
        print(f"   {status} Prompt: {prompt_name}")
    
    def log_info(self, message: str, details: Optional[Dict] = None) -> None:
        """Log an informational message."""
        entry = {
            "event": "info",
            "message": message,
            "details": details or {},
        }
        self._write_log(entry)
        print(f"ℹ️  [{self.client_id}] {message}")
    
    def finalize(self, status: str = "completed") -> None:
        """
        Finalize the run and save summary.
        
        Args:
            status: Final status (completed, failed, blocked)
        """
        self.summary["completed_at"] = datetime.utcnow().isoformat()
        self.summary["status"] = status
        
        # Calculate total duration
        started = datetime.fromisoformat(self.summary["started_at"])
        completed = datetime.fromisoformat(self.summary["completed_at"])
        self.summary["total_duration_seconds"] = (completed - started).total_seconds()
        
        # Write summary file
        summary_path = self.run_dir / "run_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(self.summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 Run summary saved to {summary_path}")
        print(f"   Status: {status}")
        print(f"   Duration: {self.summary['total_duration_seconds']:.1f}s")
        print(f"   Steps completed: {len([s for s in self.summary['steps'] if s['status'] == 'completed'])}")
        print(f"   Errors: {len(self.summary['errors'])}")


def setup_run_directory(client_id: str, base_dir: str = "runs") -> Path:
    """
    Create a timestamped run directory for a client.
    
    Structure: runs/<client_id>/<YYYYMMDD_HHMM>/
    
    Returns the Path to the run directory.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    run_dir = Path(base_dir) / client_id / timestamp
    
    # Create all necessary subdirectories
    subdirs = [
        "logs",
        "input_transform",
        "plan",
        "parsed_parts",
        "stage_2_generated_parts",
        "stage_2_prepared_html",
        "stage_3_generated_html",
        "transformed",
    ]
    
    for subdir in subdirs:
        (run_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    return run_dir

