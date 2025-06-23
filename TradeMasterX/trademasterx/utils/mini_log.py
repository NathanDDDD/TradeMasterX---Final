import os
from datetime import datetime

LOG_PATH = 'TradeMasterX/mini_log.txt'

def log_event(event):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {event}\n')

def get_last_events(n=20):
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines[-n:] 