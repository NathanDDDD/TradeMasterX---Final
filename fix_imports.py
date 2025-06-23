import os
import re

EMOJI_PATTERN = re.compile(r'[\u2190-\u2BFF\u1F300-\u1F6FF\u2600-\u26FF\u2700-\u27BF]')

# List of logging methods to clean
LOG_METHODS = [
    'logger.info', 'logger.warning', 'logger.error', 'logger.debug',
    'logging.info', 'logging.warning', 'logging.error', 'logging.debug',
    'print'
]

def fix_imports_and_emojis_in_file(file_path):
    """Fix imports and remove emojis in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        original_content = content
        # Fix imports
        content = re.sub(r'from trademasterx\.', 'from new_folder.trademasterx.', content)
        content = re.sub(r'import trademasterx\.', 'import new_folder.trademasterx.', content)
        # Remove emojis from logging and print statements
        for method in LOG_METHODS:
            # Find all lines with the logging/print method
            pattern = re.compile(rf'({method}\(.*?)([\u2190-\u2BFF\u1F300-\u1F6FF\u2600-\u26FF\u2700-\u27BF]+)(.*?\))', re.UNICODE)
            content = pattern.sub(lambda m: m.group(1) + EMOJI_PATTERN.sub('', m.group(2)) + m.group(3), content)
        # Remove any remaining emojis in the file (as a last resort)
        content = EMOJI_PATTERN.sub('', content)
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports and removed emojis in: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                fix_imports_and_emojis_in_file(os.path.join(root, file))

if __name__ == "__main__":
    process_directory('new_folder/trademasterx')
    print("All imports fixed and emojis removed.") 