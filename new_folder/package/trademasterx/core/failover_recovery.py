"""
TradeMasterX 2.0 - Failover & Recovery Protocol
Phase 12: Live Trade Safety, Failovers & Risk Mitigation Systems

Crash recovery system with state snapshots and session restoration.
"""

import json
import logging
import os
import pickle
import shutil
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
import asyncio
import signal
import sys


class RecoveryManager:
    """
    System recovery and failover management
    """
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default configuration for recovery manager"""
        return {
            'recovery': {
                'snapshot_interval_seconds': 60,
                'max_snapshots': 24,
                'recovery_timeout_seconds': 300
            }        }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger("RecoveryManager")
        
        # Recovery settings
        self.snapshot_interval = self.config.get('recovery', {}).get('snapshot_interval_seconds', 60)
        self.max_snapshots = self.config.get('recovery', {}).get('max_snapshots', 24)
        self.recovery_timeout = self.config.get('recovery', {}).get('recovery_timeout_seconds', 300)
        
        # State tracking
        self.system_components = {}
        self.active_sessions = {}
        self.last_snapshot_time = None
        self._recovery_lock = threading.Lock()
        self._shutdown_requested = False
        
        # File paths
        self.snapshots_dir = Path("data/recovery/snapshots")
        self.state_file = Path("data/recovery/system_state.json")
        self.recovery_log = Path("logs/recovery.log")
        self.crash_report_dir = Path("data/recovery/crash_reports")
        
        # Ensure directories exist
        for path in [self.snapshots_dir, self.recovery_log.parent, self.crash_report_dir]:
            path.mkdir(parents=True, exist_ok=True)
            
        # Initialize recovery system
        self._initialize_recovery_system()
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        # Create alias for components for backward compatibility
        self.components = self.system_components
        
        self.logger.info("Recovery Manager initialized")
        
    def _initialize_recovery_system(self):
        """Initialize the recovery system"""
        try:
            # Load existing state if available
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    saved_state = json.load(f)
                    self.active_sessions = saved_state.get('active_sessions', {})
                    
                self.logger.info(f"[INFO] Loaded recovery state - {len(self.active_sessions)} active sessions")
            else:
                self.active_sessions = {}
                  # Clean old snapshots
            self._cleanup_old_snapshots()
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error initializing recovery system: {e}")
            
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            if hasattr(signal, 'SIGBREAK'):
                signal.signal(signal.SIGBREAK, self._signal_handler)
                
        except Exception as e:
            self.logger.error(f"[ERROR] Error setting up signal handlers: {e}")
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"[RECOVERY] Received signal {signum} - initiating graceful shutdown")
        self._shutdown_requested = True
        self.create_emergency_snapshot("signal_shutdown")
        
    def register_component(self, component_name: str, initial_state: Any, 
                          state_setter: Callable) -> Dict[str, Any]:
        """
        Register a system component for recovery tracking
        
        Args:
            component_name: Name of the component
            initial_state: Initial state of the component
            state_setter: Function to restore component state
            
        Returns:
            Dict containing success status and component info
        """
        try:
            # Create state getter function from initial state
            state_getter = lambda: self.system_components[component_name].get('current_state', initial_state)
            
            self.system_components[component_name] = {
                'instance': None,  # Not needed for this interface
                'state_getter': state_getter,
                'state_setter': state_setter,
                'current_state': initial_state,
                'last_state': None,
                'registered_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"Registered component for recovery: {component_name}")
            
            return {
                'success': True,
                'component_name': component_name,
                'registered_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error registering component {component_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def start_session(self, session_id: str, session_data: Dict[str, Any]):
        """
        Start tracking a new session
        
        Args:
            session_id: Unique session identifier
            session_data: Session initialization data
        """
        try:
            self.active_sessions[session_id] = {
                'id': session_id,
                'start_time': datetime.now().isoformat(),
                'data': session_data,
                'status': 'active',
                'last_snapshot': None,
                'recovery_count': 0
            }
            
            self._save_system_state()
            
            self.logger.info(f"[INFO] Started session tracking: {session_id}")
            
        except Exception as e:
            self.logger.error(f"Error starting session {session_id}: {e}")
            
    def end_session(self, session_id: str):
        """
        End session tracking
        
        Args:
            session_id: Session to end
        """
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['status'] = 'completed'
                self.active_sessions[session_id]['end_time'] = datetime.now().isoformat()
                  # Remove from active tracking after a delay
                del self.active_sessions[session_id]
                
                self._save_system_state()
                
                self.logger.info(f"Ended session tracking: {session_id}")
                
        except Exception as e:
            self.logger.error(f"Error ending session {session_id}: {e}")
            
    def create_snapshot(self, reason: str = "scheduled") -> Dict[str, Any]:
        """
        Create a system state snapshot
        
        Args:
            reason: Reason for snapshot creation
            
        Returns:
            Dict: Result with success flag and snapshot_id
        """
        with self._recovery_lock:
            try:
                timestamp = datetime.now()
                snapshot_id = timestamp.strftime("%Y%m%d_%H%M%S")
                snapshot_file = self.snapshots_dir / f"snapshot_{snapshot_id}.pkl"
                
                # Collect system state
                system_state = {
                    'timestamp': timestamp.isoformat(),
                    'reason': reason,
                    'components': {},
                    'sessions': self.active_sessions.copy(),
                    'config': self.config.copy()
                }
                
                # Get state from registered components
                for name, component in self.system_components.items():
                    try:
                        state = component['state_getter']()
                        system_state['components'][name] = state
                        component['last_state'] = state
                    except Exception as e:
                        self.logger.error(f"Error getting state from {name}: {e}")
                        system_state['components'][name] = {'error': str(e)}
                        
                # Save snapshot
                with open(snapshot_file, 'wb') as f:
                    pickle.dump(system_state, f)
                    
                # Also save as JSON for inspection
                json_file = self.snapshots_dir / f"snapshot_{snapshot_id}.json"
                with open(json_file, 'w') as f:
                    # Create JSON-serializable version
                    json_state = {
                        'timestamp': system_state['timestamp'],
                        'reason': system_state['reason'],
                        'sessions': system_state['sessions'],
                        'component_count': len(system_state['components'])                    }
                    json.dump(json_state, f, indent=2)
                    
                self.last_snapshot_time = timestamp
                
                # Cleanup old snapshots
                self._cleanup_old_snapshots()
                
                self.logger.info(f"Created snapshot: {snapshot_id} ({reason})")
                return {"success": True, "snapshot_id": snapshot_id}
                
            except Exception as e:
                self.logger.error(f"Error creating snapshot: {e}")
                return {"success": False, "error": str(e)}
                
    def create_emergency_snapshot(self, reason: str = "emergency"):
        """Create emergency snapshot during crash or shutdown"""
        try:
            self.logger.critical(f"Creating emergency snapshot: {reason}")
            return self.create_snapshot(f"emergency_{reason}")
        except Exception as e:
            self.logger.critical(f"Failed to create emergency snapshot: {e}")
            return False
            
    def recover_from_crash(self, session_id: Optional[str] = None) -> bool:
        """
        Recover system from crash using latest snapshot
        
        Args:
            session_id: Specific session to recover (if None, recover all)
            
        Returns:
            bool: True if recovery successful
        """
        try:
            self.logger.info("Starting crash recovery...")
            
            # Find latest snapshot
            snapshot_file = self._find_latest_snapshot()
            if not snapshot_file:
                self.logger.error("[ERROR] No snapshots found for recovery")
                return False
                
            # Load snapshot
            with open(snapshot_file, 'rb') as f:
                system_state = pickle.load(f)
                
            self.logger.info(f"[INFO] Loading snapshot from {system_state['timestamp']}")
            
            # Restore component states
            recovery_success = True
            for name, component in self.system_components.items():
                try:
                    if name in system_state['components']:
                        component_state = system_state['components'][name]
                        if 'error' not in component_state:
                            component['state_setter'](component_state)
                            self.logger.info(f"✅ Restored component: {name}")
                        else:                            self.logger.warning(f"[WARNING] Skipped component with error: {name}")
                    else:
                        self.logger.warning(f"[WARNING] No state found for component: {name}")
                except Exception as e:
                    self.logger.error(f"[ERROR] Error restoring component {name}: {e}")
                    recovery_success = False
                    
            # Restore sessions
            if session_id:
                # Restore specific session
                if session_id in system_state['sessions']:
                    self.active_sessions[session_id] = system_state['sessions'][session_id]
                    self.active_sessions[session_id]['recovery_count'] += 1
                    self.active_sessions[session_id]['last_recovery'] = datetime.now().isoformat()
                    self.logger.info(f"✅ Restored session: {session_id}")
                else:
                    self.logger.error(f"[ERROR] Session {session_id} not found in snapshot")
                    recovery_success = False
            else:
                # Restore all sessions
                for sid, session_data in system_state['sessions'].items():
                    session_data['recovery_count'] = session_data.get('recovery_count', 0) + 1
                    session_data['last_recovery'] = datetime.now().isoformat()
                    self.active_sessions[sid] = session_data
                    
            # Save restored state
            self._save_system_state()
            
            # Create recovery report
            self._create_recovery_report(system_state, recovery_success)
            
            if recovery_success:
                self.logger.info("✅ Crash recovery completed successfully")
            else:
                self.logger.warning("[WARNING] Crash recovery completed with errors")
                
            return recovery_success
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error during crash recovery: {e}")
            return False
            
    def recover_from_snapshot(self, snapshot_id: str) -> bool:
        """
        Recover system from a specific snapshot
        
        Args:
            snapshot_id: ID of the snapshot to recover from
            
        Returns:
            bool: True if recovery successful
        """
        try:
            snapshot_file = self.snapshots_dir / f"snapshot_{snapshot_id}.pkl"
            if not snapshot_file.exists():
                self.logger.error(f"Snapshot file not found: {snapshot_id}")
                return False
                
            # Load snapshot
            with open(snapshot_file, 'rb') as f:
                system_state = pickle.load(f)
                
            self.logger.info(f"Recovering from snapshot: {snapshot_id}")
            
            # Restore component states
            for name, component in self.system_components.items():
                try:
                    if name in system_state['components']:
                        component_state = system_state['components'][name]
                        if 'error' not in component_state:
                            component['state_setter'](component_state)
                            self.logger.info(f"Restored component: {name}")
                        else:
                            self.logger.warning(f"Skipped component with error: {name}")
                    else:
                        self.logger.warning(f"Component {name} not found in snapshot")
                except Exception as e:
                    self.logger.error(f"Error restoring component {name}: {e}")
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error recovering from snapshot {snapshot_id}: {e}")
            return False
            
    def get_recovery_status(self) -> Dict[str, Any]:
        """Get current recovery system status"""
        try:
            latest_snapshot = self._find_latest_snapshot()
            
            return {
                'recovery_system_active': True,
                'registered_components': len(self.system_components),
                'active_sessions': len(self.active_sessions),
                'last_snapshot_time': self.last_snapshot_time.isoformat() if self.last_snapshot_time else None,
                'latest_snapshot_file': str(latest_snapshot) if latest_snapshot else None,
                'snapshot_interval_seconds': self.snapshot_interval,
                'snapshots_available': len(list(self.snapshots_dir.glob("snapshot_*.pkl"))),
                'shutdown_requested': self._shutdown_requested
            }
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error getting recovery status: {e}")
            return {'error': str(e)}
            
    def list_available_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots"""
        try:
            snapshots = []
            
            for snapshot_file in sorted(self.snapshots_dir.glob("snapshot_*.pkl")):
                try:
                    # Get JSON metadata if available
                    json_file = snapshot_file.with_suffix('.json')
                    if json_file.exists():
                        with open(json_file, 'r') as f:
                            metadata = json.load(f)
                    else:
                        metadata = {
                            'timestamp': 'unknown',
                            'reason': 'unknown',
                            'component_count': 0
                        }
                        
                    snapshots.append({
                        'filename': snapshot_file.name,
                        'filepath': str(snapshot_file),
                        'size_bytes': snapshot_file.stat().st_size,
                        'timestamp': metadata.get('timestamp'),
                        'reason': metadata.get('reason'),
                        'component_count': metadata.get('component_count')
                    })
                    
                except Exception as e:
                    self.logger.error(f"[ERROR] Error reading snapshot {snapshot_file}: {e}")
                    
            return snapshots
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error listing snapshots: {e}")
            return []
            
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """Alias for list_available_snapshots for compatibility with test suite"""
        return self.list_available_snapshots()
        
    def _find_latest_snapshot(self) -> Optional[Path]:
        """Find the most recent snapshot file"""
        try:
            snapshot_files = list(self.snapshots_dir.glob("snapshot_*.pkl"))
            if not snapshot_files:
                return None
                
            # Sort by modification time
            return max(snapshot_files, key=lambda f: f.stat().st_mtime)
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error finding latest snapshot: {e}")
            return None
            
    def _cleanup_old_snapshots(self):
        """Remove old snapshots beyond retention limit"""
        try:
            snapshot_files = sorted(
                self.snapshots_dir.glob("snapshot_*.pkl"),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            
            # Remove excess snapshots
            for old_snapshot in snapshot_files[self.max_snapshots:]:
                try:
                    old_snapshot.unlink()
                    # Also remove corresponding JSON file
                    json_file = old_snapshot.with_suffix('.json')
                    if json_file.exists():
                        json_file.unlink()
                    self.logger.debug(f"[DEBUG] Removed old snapshot: {old_snapshot.name}")
                except Exception as e:
                    self.logger.error(f"[ERROR] Error removing old snapshot: {e}")
                    
        except Exception as e:
            self.logger.error(f"[ERROR] Error cleaning up old snapshots: {e}")
            
    def _save_system_state(self):
        """Save current system state to file"""
        try:
            state_data = {
                'active_sessions': self.active_sessions,
                'last_updated': datetime.now().isoformat(),
                'component_count': len(self.system_components)
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"[ERROR] Error saving system state: {e}")
            
    def _create_recovery_report(self, system_state: Dict[str, Any], success: bool):
        """Create recovery report"""
        try:
            report_file = self.crash_report_dir / f"recovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            report = {
                'recovery_timestamp': datetime.now().isoformat(),
                'snapshot_timestamp': system_state['timestamp'],
                'snapshot_reason': system_state['reason'],
                'recovery_success': success,
                'components_restored': len(system_state['components']),
                'sessions_restored': len(system_state['sessions']),
                'registered_components': list(self.system_components.keys())
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
                
            self.logger.info(f"📋 Recovery report created: {report_file.name}")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error creating recovery report: {e}")
            
    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest system snapshot data
        
        Returns:
            Dict containing latest snapshot data or None if no snapshots exist
        """
        try:
            snapshot_file = self._find_latest_snapshot()
            if not snapshot_file:
                self.logger.warning("No snapshots found")
                return None
                
            # Load snapshot
            with open(snapshot_file, 'rb') as f:
                system_state = pickle.load(f)
                
            self.logger.info(f"Retrieved latest snapshot from {system_state['timestamp']}")
            return system_state
            
        except Exception as e:
            self.logger.error(f"Error retrieving latest snapshot: {e}")
            return None


class FailoverCLI:
    """
    Command-line interface for failover and recovery operations
    """
    
    def __init__(self):
        # Mock config for CLI
        config = {
            "recovery": {
                "snapshot_interval_seconds": 60,
                "max_snapshots": 24,
                "recovery_timeout_seconds": 300
            }
        }
        self.recovery_manager = RecoveryManager(config)
        
    def status(self):
        """Display recovery system status"""
        status = self.recovery_manager.get_recovery_status()
        
        print("\n🔄 RECOVERY SYSTEM STATUS")
        print("=" * 50)
        print(f"System Active: {'YES' if status.get('recovery_system_active') else 'NO'}")
        print(f"Registered Components: {status.get('registered_components', 0)}")
        print(f"Active Sessions: {status.get('active_sessions', 0)}")
        print(f"Last Snapshot: {status.get('last_snapshot_time', 'Never')}")
        print(f"Available Snapshots: {status.get('snapshots_available', 0)}")
        print(f"Snapshot Interval: {status.get('snapshot_interval_seconds', 0)}s")
        print("=" * 50)
        
    def list_snapshots(self):
        """List available snapshots"""
        snapshots = self.recovery_manager.list_available_snapshots()
        
        print("\n📸 AVAILABLE SNAPSHOTS")
        print("=" * 70)
        
        if not snapshots:
            print("No snapshots available")
        else:
            for snapshot in snapshots:
                print(f"[{snapshot['timestamp']}] {snapshot['filename']}")
                print(f"  Reason: {snapshot['reason']}")
                print(f"  Size: {snapshot['size_bytes']:,} bytes")
                print(f"  Components: {snapshot['component_count']}")
                print()
                
        print("=" * 70)
        
    def create_snapshot(self, reason: str = "Manual CLI snapshot"):
        """Create a manual snapshot"""
        if self.recovery_manager.create_snapshot(reason):
            print("✅ Snapshot created successfully")
        else:
            print("[ERROR] Failed to create snapshot")
            
    def recover(self, session_id: Optional[str] = None):
        """Initiate crash recovery"""
        print("🔄 Starting crash recovery...")
        
        if self.recovery_manager.recover_from_crash(session_id):
            print("✅ Recovery completed successfully")
        else:
            print("[ERROR] Recovery failed")


if __name__ == "__main__":
    import sys
    
    cli = FailoverCLI()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python failover_recovery.py status")
        print("  python failover_recovery.py snapshots")
        print("  python failover_recovery.py create_snapshot [reason]")
        print("  python failover_recovery.py recover [session_id]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "status":
        cli.status()
    elif command == "snapshots":
        cli.list_snapshots()
    elif command == "create_snapshot":
        reason = sys.argv[2] if len(sys.argv) > 2 else "Manual CLI snapshot"
        cli.create_snapshot(reason)
    elif command == "recover":
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        cli.recover(session_id)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
