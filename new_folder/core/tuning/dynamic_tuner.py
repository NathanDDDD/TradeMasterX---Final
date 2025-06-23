"""
TradeMasterX 2.0 - Dynamic System Tuner
Phase 9B Task 2: Adaptive confidence threshold adjustment
"""

import logging
from datetime import datetime
from typing import Dict, Optional

class DynamicSystemTuner:
    """
    Dynamic system tuning based on performance metrics
    Adaptive confidence threshold adjustment
    """
    
    def __init__(self, initial_confidence: float = 0.75):
        self.current_confidence_threshold = initial_confidence
        self.logger = logging.getLogger("DynamicTuner")
        self.adjustment_step = 0.02
        
    def get_current_confidence_threshold(self) -> float:
        """Get current confidence threshold"""
        return self.current_confidence_threshold
    
    def update_performance_metrics(self, metrics: Dict):
        """Update with latest performance metrics"""
        self.latest_metrics = metrics
    
    def check_adaptive_adjustments(self) -> Optional[Dict]:
        """Check if adaptive adjustments are needed"""
        if not hasattr(self, 'latest_metrics'):
            return None
            
        accuracy = self.latest_metrics.get('trade_accuracy', 0)
        
        adjustments = {}
        
        # Adjust confidence threshold based on accuracy
        if accuracy >= 0.80:  # High accuracy - increase threshold
            old_threshold = self.current_confidence_threshold
            self.current_confidence_threshold = min(0.95, self.current_confidence_threshold + self.adjustment_step)
            if self.current_confidence_threshold != old_threshold:
                adjustments['confidence_threshold'] = {
                    'old': old_threshold,
                    'new': self.current_confidence_threshold,
                    'reason': 'High accuracy - increased threshold'
                }
        elif accuracy <= 0.65:  # Low accuracy - decrease threshold
            old_threshold = self.current_confidence_threshold
            self.current_confidence_threshold = max(0.50, self.current_confidence_threshold - self.adjustment_step)
            if self.current_confidence_threshold != old_threshold:
                adjustments['confidence_threshold'] = {
                    'old': old_threshold,
                    'new': self.current_confidence_threshold,
                    'reason': 'Low accuracy - decreased threshold'
                }
        
        return adjustments if adjustments else None
    
    def update_retraining_status(self, validation_result: Dict):
        """Update with retraining validation results"""
        self.logger.info(f"🔄 Retraining status updated: {validation_result.get('status', 'UNKNOWN')}")
