#!/usr/bin/env python3
"""
Directory Merger for TradeMasterX
Merges nested directories into a clean, organized structure
"""

import os
import shutil
import glob
from pathlib import Path

def merge_directories():
    """Merge the nested directory structure"""
    print("TradeMasterX Directory Merger")
    print("=" * 40)
    
    # Get current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Check if we're in the right place
    if not (current_dir / "New folder").exists():
        print("ERROR: 'New folder' directory not found!")
        print("Please run this script from the parent directory of 'New folder'")
        return False
    
    # Create a clean project directory
    project_dir = current_dir / "trademasterx_clean"
    if project_dir.exists():
        shutil.rmtree(project_dir)
    project_dir.mkdir()
    
    print(f"Creating clean project at: {project_dir}")
    
    # Copy all files from New folder to the clean directory
    source_dir = current_dir / "New folder"
    
    # Copy main application files
    main_files = [
        "main_app.py",
        "main_app_clean.py", 
        "launch_app.py",
        "start_dashboard.py",
        "requirements.txt",
        "setup.py",
        "README.md"
    ]
    
    for file_name in main_files:
        source_file = source_dir / file_name
        if source_file.exists():
            shutil.copy2(source_file, project_dir)
            print(f"Copied: {file_name}")
    
    # Copy important directories
    important_dirs = [
        "trademasterx",
        "config", 
        "data",
        "logs",
        "logs_clean",
        "reports",
        "reports_clean",
        "desktop_app",
        "tests"
    ]
    
    for dir_name in important_dirs:
        source_path = source_dir / dir_name
        if source_path.exists():
            dest_path = project_dir / dir_name
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(source_path, dest_path)
            print(f"Copied directory: {dir_name}")
    
    # Copy important Python files (excluding duplicates)
    python_files = glob.glob(str(source_dir / "*.py"))
    for py_file in python_files:
        file_name = Path(py_file).name
        if file_name not in main_files:  # Don't copy main files twice
            dest_file = project_dir / file_name
            if not dest_file.exists():
                shutil.copy2(py_file, dest_file)
                print(f"Copied: {file_name}")
    
    # Copy important documentation and config files
    doc_files = glob.glob(str(source_dir / "*.md"))
    for doc_file in doc_files:
        file_name = Path(doc_file).name
        dest_file = project_dir / file_name
        if not dest_file.exists():
            shutil.copy2(doc_file, dest_file)
            print(f"Copied: {file_name}")
    
    # Copy JSON and YAML config files
    config_files = glob.glob(str(source_dir / "*.json")) + glob.glob(str(source_dir / "*.yaml"))
    for config_file in config_files:
        file_name = Path(config_file).name
        dest_file = project_dir / file_name
        if not dest_file.exists():
            shutil.copy2(config_file, dest_file)
            print(f"Copied: {file_name}")
    
    # Create a simple launcher script
    launcher_content = '''#!/usr/bin/env python3
"""
TradeMasterX Clean Launcher
Simple launcher for the cleaned project
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def main():
    """Main launcher function"""
    print("TradeMasterX Clean Project")
    print("=" * 30)
    
    # Check if main app exists
    if not (current_dir / "main_app_clean.py").exists():
        print("ERROR: main_app_clean.py not found!")
        return 1
    
    try:
        # Import and run the main app
        from main_app_clean import main as app_main
        return app_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Try running: python main_app_clean.py")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    launcher_file = project_dir / "run.py"
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print(f"Created launcher: run.py")
    
    # Create a README for the clean project
    readme_content = '''# TradeMasterX Clean Project

This is a cleaned and organized version of the TradeMasterX trading application.

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python run.py
   ```
   
   Or directly:
   ```
   python main_app_clean.py
   ```

3. Start the dashboard:
   ```
   python start_dashboard.py
   ```

## Main Files

- `main_app_clean.py` - Main application (clean version)
- `launch_app.py` - Application launcher
- `start_dashboard.py` - Dashboard component
- `run.py` - Simple launcher script

## Directory Structure

- `trademasterx/` - Core application modules
- `config/` - Configuration files
- `data/` - Data storage
- `logs/` - Application logs
- `reports/` - Generated reports
- `desktop_app/` - Desktop GUI application
- `tests/` - Test files

## Features

- AI-powered trading system
- Real-time monitoring dashboard
- Machine learning optimization
- Anomaly detection
- Web interface
- Desktop GUI

For more information, see the original documentation files.
'''
    
    readme_file = project_dir / "README_CLEAN.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"Created documentation: README_CLEAN.md")
    
    print("\n" + "=" * 40)
    print("DIRECTORY MERGE COMPLETE!")
    print(f"Clean project created at: {project_dir}")
    print("\nNext steps:")
    print(f"1. cd {project_dir}")
    print("2. pip install -r requirements.txt")
    print("3. python run.py")
    print("=" * 40)
    
    return True

if __name__ == "__main__":
    success = merge_directories()
    if not success:
        print("Directory merge failed!")
        exit(1) 