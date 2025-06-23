"""
TradeMasterX 2.0 - Phase 9B Task 4: Complete RetrainingValidator
Real-time model validation with rollback capabilities and stalled training detection
"""

import time
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import joblib
from dataclasses import dataclass


@dataclass
class ValidationMetrics:
    """Model validation performance metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confidence_avg: float
    prediction_count: int
    timestamp: datetime


@dataclass
class ModelVersion:
    """Model version tracking"""
    version_id: str
    model_path: str
    metrics: ValidationMetrics
    creation_time: datetime
    is_active: bool


class RetrainingValidator:
    """
    Validates retrained models and handles rollbacks
    - Monitors prediction accuracy vs baseline
    - Detects stalled/failed training
    - Implements automatic model rollback
    - Manages model version history
    """
    
    def __init__(self, config_path: str = "config/validation_config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        
        # Validation thresholds
        self.min_improvement_threshold = self.config.get("min_improvement_threshold", 0.02)  # 2%
        self.max_performance_drop = self.config.get("max_performance_drop", 0.05)  # 5%
        self.stall_timeout_hours = self.config.get("stall_timeout_hours", 6)
        self.min_predictions_for_validation = self.config.get("min_predictions", 50)
        
        # Model management
        self.model_versions: List[ModelVersion] = []
        self.current_model_version = None
        self.baseline_metrics = None
        
        # Validation state
        self.validation_history = []
        self.last_training_start = None
        self.training_stall_detected = False
        
        # Flags for system communication
        self.RETRAINING_STALLED = False
        self.MODEL_ROLLBACK_TRIGGERED = False
        self.VALIDATION_FAILED = False
        
        self.logger.info("RetrainingValidator initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load validation configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                "min_improvement_threshold": 0.02,
                "max_performance_drop": 0.05,
                "stall_timeout_hours": 6,
                "min_predictions": 50,
                "model_storage_path": "models/versions/",
                "validation_log_path": "logs/validation.log"
            }
    
    def _setup_logger(self) -> logging.Logger:
        """Setup validation logger"""
        logger = logging.getLogger("RetrainingValidator")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler("logs/validation.log")
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def register_baseline_model(self, model_path: str, baseline_metrics: ValidationMetrics):
        """Register the initial baseline model for comparison"""
        version_id = f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        baseline_version = ModelVersion(
            version_id=version_id,
            model_path=model_path,
            metrics=baseline_metrics,
            creation_time=datetime.now(),
            is_active=True
        )
        
        self.model_versions.append(baseline_version)
        self.current_model_version = baseline_version
        self.baseline_metrics = baseline_metrics
        
        self.logger.info(f"Baseline model registered: {version_id}")
        self.logger.info(f"Baseline accuracy: {baseline_metrics.accuracy:.4f}")
    
    def notify_training_started(self):
        """Notify validator that model retraining has started"""
        self.last_training_start = datetime.now()
        self.training_stall_detected = False
        self.RETRAINING_STALLED = False
        
        self.logger.info("Model retraining started - validation monitoring active")
    
    def validate_new_model(self, model_path: str, 
                          validation_predictions: List[Dict],
                          validation_actual: List[int]) -> bool:
        """
        Validate a newly retrained model
        
        Args:
            model_path: Path to the new model file
            validation_predictions: List of prediction results with confidence
            validation_actual: List of actual outcomes (0 or 1)
            
        Returns:
            bool: True if model passes validation, False if rollback needed
        """
        if len(validation_predictions) < self.min_predictions_for_validation:
            self.logger.warning(f"Insufficient predictions for validation: {len(validation_predictions)}")
            return False
        
        # Calculate validation metrics
        new_metrics = self._calculate_metrics(validation_predictions, validation_actual)
        
        # Create new model version
        version_id = f"retrained_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        new_version = ModelVersion(
            version_id=version_id,
            model_path=model_path,
            metrics=new_metrics,
            creation_time=datetime.now(),
            is_active=False  # Not active until validated
        )
        
        # Validate against current model
        validation_passed = self._validate_against_current(new_metrics)
        
        if validation_passed:
            # Accept new model
            self._accept_new_model(new_version)
            return True
        else:
            # Reject and potentially rollback
            self._reject_new_model(new_version)
            return False
    
    def _calculate_metrics(self, predictions: List[Dict], 
                          actual: List[int]) -> ValidationMetrics:
        """Calculate validation metrics from predictions"""
        # Extract predictions and confidences
        pred_values = [p['prediction'] for p in predictions]
        confidences = [p['confidence'] for p in predictions]
        
        # Calculate accuracy
        correct = sum(1 for p, a in zip(pred_values, actual) if p == a)
        accuracy = correct / len(actual)
        
        # Calculate precision, recall, F1
        tp = sum(1 for p, a in zip(pred_values, actual) if p == 1 and a == 1)
        fp = sum(1 for p, a in zip(pred_values, actual) if p == 1 and a == 0)
        fn = sum(1 for p, a in zip(pred_values, actual) if p == 0 and a == 1)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Average confidence
        confidence_avg = np.mean(confidences)
        
        return ValidationMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            confidence_avg=confidence_avg,
            prediction_count=len(predictions),
            timestamp=datetime.now()
        )
    
    def _validate_against_current(self, new_metrics: ValidationMetrics) -> bool:
        """Validate new model against current model performance"""
        if not self.current_model_version:
            self.logger.warning("No current model for comparison - accepting new model")
            return True
        
        current_metrics = self.current_model_version.metrics
        
        # Check for significant performance drop
        accuracy_drop = current_metrics.accuracy - new_metrics.accuracy
        if accuracy_drop > self.max_performance_drop:
            self.logger.error(f"Significant accuracy drop detected: {accuracy_drop:.4f}")
            self.VALIDATION_FAILED = True
            return False
        
        # Check for minimum improvement (if not baseline)
        if len(self.model_versions) > 1:  # Not the first retrained model
            improvement = new_metrics.accuracy - current_metrics.accuracy
            if improvement < self.min_improvement_threshold:
                self.logger.warning(f"Insufficient improvement: {improvement:.4f}")
                return False
        
        # Additional validation checks
        if new_metrics.precision < 0.4 or new_metrics.recall < 0.4:
            self.logger.error(f"Poor precision/recall: {new_metrics.precision:.4f}/{new_metrics.recall:.4f}")
            return False
        
        return True
    
    def _accept_new_model(self, new_version: ModelVersion):
        """Accept and activate new model version"""
        # Deactivate current model
        if self.current_model_version:
            self.current_model_version.is_active = False
        
        # Activate new model
        new_version.is_active = True
        self.model_versions.append(new_version)
        self.current_model_version = new_version
        
        # Reset flags
        self.VALIDATION_FAILED = False
        self.MODEL_ROLLBACK_TRIGGERED = False
        
        # Log acceptance
        self.logger.info(f"✅ New model accepted: {new_version.version_id}")
        self.logger.info(f"New accuracy: {new_version.metrics.accuracy:.4f}")
        
        # Save validation record
        self._save_validation_record(new_version, accepted=True)
    
    def _reject_new_model(self, rejected_version: ModelVersion):
        """Reject new model and handle rollback if necessary"""
        self.logger.error(f"❌ Model rejected: {rejected_version.version_id}")
        self.logger.error(f"Rejected accuracy: {rejected_version.metrics.accuracy:.4f}")
        
        # Save rejection record
        self._save_validation_record(rejected_version, accepted=False)
        
        # Check if rollback is needed
        if self._should_trigger_rollback():
            self._trigger_model_rollback()
    
    def _should_trigger_rollback(self) -> bool:
        """Determine if model rollback should be triggered"""
        # Count recent failures
        recent_failures = 0
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for record in self.validation_history:
            if record['timestamp'] > cutoff_time and not record['accepted']:
                recent_failures += 1
        
        # Trigger rollback if multiple recent failures
        return recent_failures >= 2
    
    def _trigger_model_rollback(self):
        """Trigger rollback to previous stable model"""
        # Find last stable model (not current)
        stable_models = [v for v in self.model_versions 
                        if not v.is_active and v != self.current_model_version]
        
        if not stable_models:
            self.logger.error("No stable model available for rollback!")
            return
        
        # Get most recent stable model
        rollback_model = max(stable_models, key=lambda x: x.creation_time)
        
        # Deactivate current model
        if self.current_model_version:
            self.current_model_version.is_active = False
        
        # Activate rollback model
        rollback_model.is_active = True
        self.current_model_version = rollback_model
        
        # Set rollback flag
        self.MODEL_ROLLBACK_TRIGGERED = True
        
        self.logger.critical(f"🔄 MODEL ROLLBACK TRIGGERED")
        self.logger.critical(f"Rolled back to: {rollback_model.version_id}")
        self.logger.critical(f"Rollback accuracy: {rollback_model.metrics.accuracy:.4f}")
    
    def check_for_stalled_training(self) -> bool:
        """
        Check if model training has stalled and handle accordingly
        
        Returns:
            bool: True if stalled training was detected and handled
        """
        if not self.last_training_start:
            return False
        
        # Check if training has been running too long
        training_duration = datetime.now() - self.last_training_start
        
        if training_duration.total_seconds() > (self.stall_timeout_hours * 3600):
            if not self.training_stall_detected:
                self.training_stall_detected = True
                self.RETRAINING_STALLED = True
                return self._handle_stalled_training()
        
        return False
    
    def _handle_stalled_training(self) -> bool:
        """
        Handle stalled training situation
        
        Returns:
            bool: True if stall was successfully handled
        """
        self.logger.critical("🚨 TRAINING STALL DETECTED")
        self.logger.critical(f"Training started: {self.last_training_start}")
        self.logger.critical(f"Duration: {datetime.now() - self.last_training_start}")
        
        # Set system flags
        self.RETRAINING_STALLED = True
        
        # Record stall event
        stall_record = {
            'event_type': 'training_stall',
            'timestamp': datetime.now().isoformat(),
            'training_start': self.last_training_start.isoformat(),
            'duration_hours': (datetime.now() - self.last_training_start).total_seconds() / 3600,
            'current_model': self.current_model_version.version_id if self.current_model_version else None
        }
        
        # Save stall record
        self._save_stall_record(stall_record)
        
        # Attempt recovery actions
        recovery_success = self._attempt_training_recovery()
        
        if recovery_success:
            self.logger.info("✅ Training stall recovery successful")
            self.RETRAINING_STALLED = False
            self.training_stall_detected = False
            return True
        else:
            self.logger.error("❌ Training stall recovery failed")
            # Keep flags set for external intervention
            return False
    
    def _attempt_training_recovery(self) -> bool:
        """
        Attempt to recover from stalled training
        
        Returns:
            bool: True if recovery was successful
        """
        try:
            # Recovery strategy 1: Check if model file exists and is valid
            if self.current_model_version:
                model_path = self.current_model_version.model_path
                if Path(model_path).exists():
                    # Try to load the model to verify it's not corrupted
                    try:
                        test_model = joblib.load(model_path)
                        self.logger.info("Current model file is valid - continuing with existing model")
                        
                        # Reset training state
                        self.last_training_start = None
                        return True
                    except Exception as e:
                        self.logger.error(f"Current model file corrupted: {e}")
            
            # Recovery strategy 2: Rollback to previous stable model
            stable_models = [v for v in self.model_versions 
                           if v != self.current_model_version and Path(v.model_path).exists()]
            
            if stable_models:
                # Get most recent stable model
                stable_model = max(stable_models, key=lambda x: x.creation_time)
                
                # Verify the stable model is loadable
                try:
                    test_model = joblib.load(stable_model.model_path)
                    
                    # Activate stable model
                    if self.current_model_version:
                        self.current_model_version.is_active = False
                    
                    stable_model.is_active = True
                    self.current_model_version = stable_model
                    
                    self.logger.info(f"Recovered using stable model: {stable_model.version_id}")
                    
                    # Reset training state
                    self.last_training_start = None
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Stable model not loadable: {e}")
            
            # Recovery strategy 3: Use baseline model if available
            if self.baseline_metrics and len(self.model_versions) > 0:
                baseline_model = self.model_versions[0]  # First model is baseline
                if Path(baseline_model.model_path).exists():
                    try:
                        test_model = joblib.load(baseline_model.model_path)
                        
                        # Activate baseline model
                        if self.current_model_version:
                            self.current_model_version.is_active = False
                        
                        baseline_model.is_active = True
                        self.current_model_version = baseline_model
                        
                        self.logger.info(f"Recovered using baseline model: {baseline_model.version_id}")
                        
                        # Reset training state
                        self.last_training_start = None
                        return True
                        
                    except Exception as e:
                        self.logger.error(f"Baseline model not loadable: {e}")
            
            # All recovery strategies failed
            self.logger.error("All recovery strategies failed - manual intervention required")
            return False
            
        except Exception as e:
            self.logger.error(f"Training recovery attempt failed: {e}")
            return False
    
    def _save_validation_record(self, model_version: ModelVersion, accepted: bool):
        """Save validation record to history"""
        record = {
            'timestamp': datetime.now(),
            'version_id': model_version.version_id,
            'accuracy': model_version.metrics.accuracy,
            'precision': model_version.metrics.precision,
            'recall': model_version.metrics.recall,
            'f1_score': model_version.metrics.f1_score,
            'accepted': accepted
        }
        
        self.validation_history.append(record)
        
        # Keep only last 100 records
        if len(self.validation_history) > 100:
            self.validation_history = self.validation_history[-100:]
    
    def _save_stall_record(self, stall_record: Dict):
        """Save training stall record to file"""
        stall_file = Path("logs/training_stalls.json")
        
        # Load existing records
        stall_records = []
        if stall_file.exists():
            try:
                with open(stall_file, 'r') as f:
                    stall_records = json.load(f)
            except:
                stall_records = []
        
        # Add new record
        stall_records.append(stall_record)
        
        # Save updated records
        with open(stall_file, 'w') as f:
            json.dump(stall_records, f, indent=2)
    
    def get_validation_status(self) -> Dict:
        """Get current validation status for monitoring"""
        status = {
            'current_model': self.current_model_version.version_id if self.current_model_version else None,
            'current_accuracy': self.current_model_version.metrics.accuracy if self.current_model_version else None,
            'total_models': len(self.model_versions),
            'validation_history_count': len(self.validation_history),
            'flags': {
                'RETRAINING_STALLED': self.RETRAINING_STALLED,
                'MODEL_ROLLBACK_TRIGGERED': self.MODEL_ROLLBACK_TRIGGERED,
                'VALIDATION_FAILED': self.VALIDATION_FAILED
            },
            'last_training_start': self.last_training_start.isoformat() if self.last_training_start else None,
            'training_stall_detected': self.training_stall_detected,
            'timestamp': datetime.now().isoformat()
        }
        
        return status
    
    def get_model_performance_summary(self) -> Dict:
        """Get summary of all model performance"""
        if not self.model_versions:
            return {}
        
        summary = {
            'baseline_accuracy': self.baseline_metrics.accuracy if self.baseline_metrics else None,
            'current_accuracy': self.current_model_version.metrics.accuracy if self.current_model_version else None,
            'best_accuracy': max(v.metrics.accuracy for v in self.model_versions),
            'model_count': len(self.model_versions),
            'accepted_models': len([r for r in self.validation_history if r['accepted']]),
            'rejected_models': len([r for r in self.validation_history if not r['accepted']]),
            'models': [
                {
                    'version_id': v.version_id,
                    'accuracy': v.metrics.accuracy,
                    'precision': v.metrics.precision,
                    'recall': v.metrics.recall,
                    'is_active': v.is_active,
                    'creation_time': v.creation_time.isoformat()
                }
                for v in self.model_versions
            ]
        }
        
        return summary


# Example usage and testing
if __name__ == "__main__":
    # Initialize validator
    validator = RetrainingValidator()
    
    # Register baseline model (example)
    baseline_metrics = ValidationMetrics(
        accuracy=0.72,
        precision=0.68,
        recall=0.75,
        f1_score=0.71,
        confidence_avg=0.65,
        prediction_count=100,
        timestamp=datetime.now()
    )
    
    validator.register_baseline_model("models/baseline_model.joblib", baseline_metrics)
    
    print("✅ RetrainingValidator implementation complete!")
    print("🔍 Key features implemented:")
    print("   - Model validation against performance thresholds")
    print("   - Automatic rollback on significant performance drops")
    print("   - Stalled training detection and recovery")
    print("   - Model version management")
    print("   - Comprehensive logging and monitoring")
