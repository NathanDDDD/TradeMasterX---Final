with open('trademasterx/core/trade_deviation_alert.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the specific problematic line
content = content.replace(
    '                  self.logger.critical(f"CONSECUTIVE DEVIATION ALERT: {self.consecutive_deviations} trades with significant deviations")',
    '            self.logger.critical(f"CONSECUTIVE DEVIATION ALERT: {self.consecutive_deviations} trades with significant deviations")'
)

with open('trademasterx/core/trade_deviation_alert.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed line 335 indentation')
