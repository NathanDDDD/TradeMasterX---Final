import unittest
import os
from trademasterx.core.memory import Memory

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.test_path = 'TradeMasterX/test_memory.json'
        if os.path.exists(self.test_path):
            os.remove(self.test_path)
        self.memory = Memory(self.test_path)

    def tearDown(self):
        if os.path.exists(self.test_path):
            os.remove(self.test_path)

    def test_log_signal_and_trade(self):
        self.memory.log_signal({'test': 1})
        self.memory.log_trade({'trade': 2})
        self.assertIn('signals', self.memory.data)
        self.assertIn('trades', self.memory.data)
        self.assertEqual(self.memory.data['signals'][0], {'test': 1})
        self.assertEqual(self.memory.data['trades'][0], {'trade': 2})

if __name__ == '__main__':
    unittest.main() 