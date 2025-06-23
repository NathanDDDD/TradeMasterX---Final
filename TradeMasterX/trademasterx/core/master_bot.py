from typing import List, Dict

class MasterBot:
    """Central orchestrator for trading decisions."""
    def __init__(self, config, forms: List):
        self.config = config
        self.forms = forms
        self.memory = []  # Layered memory stub

    def collect_signals(self, market_data: Dict) -> List[Dict]:
        """Collect signals from all forms/agents."""
        signals = []
        for form in self.forms:
            signal = form.analyze(market_data)
            signals.append(signal)
        return signals

    def aggregate_signals(self, signals: List[Dict]) -> Dict:
        """Aggregate signals using weighted voting/consensus."""
        # Weighted voting/consensus
        weights = self.config.get('weights', {})
        actions = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        total_weight = 0
        reasons = []
        for i, signal in enumerate(signals):
            action = signal.get('action', 'HOLD')
            confidence = signal.get('confidence', 0.0)
            reason = signal.get('reason', '')
            form_name = self.forms[i].__class__.__name__.lower().replace('analyzer', '').replace('bot', '')
            weight = weights.get(form_name, 1.0)
            actions[action] += confidence * weight
            total_weight += weight
            reasons.append(f"{form_name}: {reason}")
        # Decision
        best_action = max(actions, key=actions.get)
        avg_conf = actions[best_action] / total_weight if total_weight else 0.0
        return {
            "action": best_action,
            "confidence": round(avg_conf, 2),
            "reason": "; ".join(reasons)
        }

    def run(self):
        """Main loop stub."""
        print("MasterBot running. (Stub)") 