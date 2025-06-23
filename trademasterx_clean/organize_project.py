#!/usr/bin/env python3
"""
TradeMasterX 2.0 - Project Structure Cleanup & Organization
Prepares the project for final packaging and PyInstaller
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict

class ProjectOrganizer:
    """Organizes TradeMasterX project structure for final packaging"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.src_dir = self.base_dir / "src"
        self.desktop_app_dir = self.base_dir / "desktop_app"
        
        # Define essential files to keep
        self.essential_files = {
            # Core application files
            "main_app.py": "Main application launcher",
            "launch_production.py": "Production launcher", 
            "simple_dashboard.py": "Web dashboard",
            "phase_14_complete_autonomous_ai.py": "Core AI system",
            
            # Configuration files
            "requirements.txt": "Python dependencies",
            "strategy_weights.json": "AI strategy weights",
            ".env.example": "Environment template",
            
            # Launch scripts
            "launch_desktop_gui.bat": "Desktop GUI launcher",
            
            # Documentation
            "README.md": "Project documentation",
            "PHASE_15_MISSION_ACCOMPLISHED.md": "Completion status"
        }
        
        # Define directories to keep
        self.essential_dirs = [
            "trademasterx",  # Core module
            "core_clean",    # Clean core components
            "desktop_app",   # Desktop GUI
            "src",          # Organized source code
            "logs",         # Application logs
            "data",         # Trading data
            "reports",      # System reports
            "config"        # Configuration files
        ]
        
        # Files to delete (redundant or temporary)
        self.cleanup_patterns = [
            "*test*.py",
            "*demo*.py", 
            "*phase_1[0-3]*.py",
            "quick_*.py",
            "integration_test.py",
            "comprehensive_test_results.txt",
            "test_output.txt",
            "*.pyc",
            "__pycache__",
            ".pytest_cache"
        ]
    
    def create_src_structure(self):
        """Create organized src/ directory structure"""
        print("📁 Creating organized src/ structure...")
        
        # Create src subdirectories
        src_dirs = [
            "src/trademasterx",
            "src/core",
            "src/gui", 
            "src/utils",
            "src/config"
        ]
        
        for dir_path in src_dirs:
            (self.base_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Copy essential files to src/
        essential_copies = {
            "main_app.py": "src/main_app.py",
            "launch_production.py": "src/launch_production.py", 
            "simple_dashboard.py": "src/simple_dashboard.py",
            "phase_14_complete_autonomous_ai.py": "src/core/autonomous_ai.py"
        }
        
        for src_file, dst_file in essential_copies.items():
            src_path = self.base_dir / src_file
            dst_path = self.base_dir / dst_file
            
            if src_path.exists():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                print(f"  ✅ Copied {src_file} → {dst_file}")
        
        # Copy trademasterx module
        if (self.base_dir / "trademasterx").exists():
            shutil.copytree(
                self.base_dir / "trademasterx",
                self.base_dir / "src" / "trademasterx",
                dirs_exist_ok=True
            )
            print("  ✅ Copied trademasterx module → src/trademasterx")
        
        # Copy desktop app
        if self.desktop_app_dir.exists():
            shutil.copytree(
                self.desktop_app_dir,
                self.base_dir / "src" / "gui" / "desktop_app", 
                dirs_exist_ok=True
            )
            print("  ✅ Copied desktop_app → src/gui/desktop_app")
        
        print("✅ Src structure created successfully!")
    
    def cleanup_redundant_files(self):
        """Remove redundant and temporary files"""
        print("🧹 Cleaning up redundant files...")
        
        cleanup_count = 0
        
        for pattern in self.cleanup_patterns:
            for file_path in self.base_dir.glob(pattern):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        print(f"  🗑️ Removed {file_path.name}")
                        cleanup_count += 1
                    except Exception as e:
                        print(f"  ❌ Could not remove {file_path.name}: {e}")
                elif file_path.is_dir():
                    try:
                        shutil.rmtree(file_path)
                        print(f"  🗑️ Removed directory {file_path.name}")
                        cleanup_count += 1
                    except Exception as e:
                        print(f"  ❌ Could not remove directory {file_path.name}: {e}")
        
        print(f"✅ Cleaned up {cleanup_count} files/directories")
    
    def create_pyinstaller_spec(self):
        """Create PyInstaller spec file for desktop app"""
        print("📦 Creating PyInstaller specification...")
        
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_app/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('desktop_app/components', 'components'),
        ('desktop_app/utils', 'utils'),
        ('desktop_app/assets', 'assets'),
        ('desktop_app/.streamlit', '.streamlit'),
        ('trademasterx', 'trademasterx'),
        ('core_clean', 'core_clean'),
        ('config', 'config'),
        ('data', 'data'),
        ('reports', 'reports'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'plotly',
        'psutil',
        'requests',
        'aiohttp',
        'asyncio',
        'json',
        'pathlib',
        'datetime',
        'threading',
        'subprocess'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TradeMasterX_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='desktop_app/assets/icon.ico'  # Add icon if available
)
'''
        
        spec_file = self.base_dir / "TradeMasterX_GUI.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        print(f"✅ PyInstaller spec created: {spec_file}")
    
    def create_build_scripts(self):
        """Create build scripts for packaging"""
        print("🔨 Creating build scripts...")
        
        # Windows build script
        build_bat = '''@echo off
echo ====================================================
echo TradeMasterX 2.0 - Building Desktop Application
echo ====================================================
echo.

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
pyinstaller TradeMasterX_GUI.spec --clean --distpath dist --workpath build

echo.
echo Build complete! Check the dist/ folder for TradeMasterX_GUI.exe
echo.
pause
'''
        
        with open(self.base_dir / "build_exe.bat", 'w') as f:
            f.write(build_bat)
        
        # Requirements for packaging
        packaging_requirements = '''# TradeMasterX 2.0 - Packaging Requirements

# Core dependencies
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.15.0
psutil>=5.9.0
requests>=2.31.0
aiohttp>=3.8.0

# Packaging
pyinstaller>=5.10.0

# Optional: For enhanced features
openai>=1.0.0
anthropic>=0.3.0
'''
        
        with open(self.base_dir / "requirements_packaging.txt", 'w') as f:
            f.write(packaging_requirements)
        
        print("✅ Build scripts created!")
    
    def create_final_documentation(self):
        """Create final user documentation"""
        print("📚 Creating final documentation...")
        
        user_guide = '''# TradeMasterX 2.0 - Desktop GUI User Guide

##  Quick Start

### Option 1: Run from Source
1. Install requirements: `pip install -r requirements.txt`
2. Launch GUI: `python -m streamlit run desktop_app/app.py`
3. Open browser to: http://localhost:8501

### Option 2: Use Batch File
1. Double-click `launch_desktop_gui.bat`
2. GUI will open automatically in your browser

### Option 3: Use Executable (if built)
1. Run `TradeMasterX_GUI.exe` from the dist/ folder
2. GUI opens as a desktop application

## 🎯 Features

### 1. System Control Panel
- **Start/Stop TradeMasterX**: Control the main trading system
- **Launch Dashboard**: Start the web dashboard on localhost:8080
- **View Logs**: Monitor system activity in real-time

### 2. AI Command Chat
- **Natural Language Interface**: Talk to your trading system
- **Quick Commands**: Pre-built buttons for common tasks
- **Smart Responses**: AI-powered responses using OpenAI or Claude

### 3. System Status Dashboard
- **Real-time Metrics**: System health, AI confidence, anomaly alerts
- **Component Status**: Monitor all system components
- **Performance Charts**: Visual performance analytics

### 4. Trade History & Analytics
- **Trade Log**: View all historical trades
- **Performance Metrics**: Win rate, returns, Sharpe ratio
- **Interactive Charts**: Visualize trading performance
- **Filter Options**: Filter by time period, confidence, strategy

### 5. Settings & Configuration
- **API Keys**: Configure OpenAI and Claude API keys
- **System Settings**: Demo mode, logging, auto-start options
- **Export/Import**: Backup and restore configurations

## 🔑 API Configuration

### OpenAI Setup
1. Get API key from: https://platform.openai.com/api-keys
2. Go to Settings → API Keys in the GUI
3. Enter your OpenAI API key
4. Click "Save API Keys"

### Claude Setup
1. Get API key from: https://console.anthropic.com/
2. Go to Settings → API Keys in the GUI  
3. Enter your Claude API key
4. Click "Save API Keys"

## 🛠️ Troubleshooting

### Common Issues

**GUI won't start:**
- Check Python installation: `python --version`
- Install requirements: `pip install -r requirements.txt`
- Try: `python -m streamlit run desktop_app/app.py`

**AI Chat not working:**
- Verify API keys are configured in Settings
- Check internet connection
- Test API keys in Settings panel

**System control not responding:**
- Ensure TradeMasterX files are present
- Check file permissions
- Try running as administrator

**Dashboard won't launch:**
- Check if port 8080 is available
- Try restarting the system control
- Check firewall settings

### Getting Help

1. Check the system logs in the GUI
2. Review error messages in the terminal
3. Ensure all requirements are installed
4. Try restarting the application

## 📦 Building Executable

To create a standalone executable:

1. Install PyInstaller: `pip install pyinstaller`
2. Run build script: `build_exe.bat`
3. Find executable in `dist/` folder

## 🎮 Usage Tips

- **Demo Mode**: Start with demo mode enabled for safe testing
- **Auto-refresh**: Enable auto-refresh on status dashboard for real-time monitoring
- **Quick Commands**: Use the quick command buttons for faster AI interaction
- **Filters**: Use trade history filters to focus on specific time periods or strategies
- **Export Config**: Regularly export your configuration as backup

## 🎯 Next Steps

1. Configure your API keys for full AI functionality
2. Start TradeMasterX system using the control panel
3. Monitor performance using the status dashboard
4. Interact with your system using the AI chat
5. Analyze your trading history and performance

Happy Trading! 
'''
        
        with open(self.base_dir / "USER_GUIDE.md", 'w') as f:
            f.write(user_guide)
        
        print("✅ User guide created!")
    
    def run_organization(self):
        """Run the complete project organization"""
        print("🎯 Starting TradeMasterX 2.0 Project Organization...")
        print("=" * 60)
        
        try:
            # Step 1: Create organized src structure
            self.create_src_structure()
            print()
            
            # Step 2: Clean up redundant files
            self.cleanup_redundant_files()
            print()
            
            # Step 3: Create PyInstaller spec
            self.create_pyinstaller_spec()
            print()
            
            # Step 4: Create build scripts
            self.create_build_scripts()
            print()
            
            # Step 5: Create documentation
            self.create_final_documentation()
            print()
            
            print("🎉 PROJECT ORGANIZATION COMPLETE!")
            print("=" * 60)
            print("✅ Organized source code in src/ directory")
            print("✅ Cleaned up redundant files")
            print("✅ Created PyInstaller packaging files") 
            print("✅ Generated build scripts")
            print("✅ Created user documentation")
            print()
            print(" NEXT STEPS:")
            print("1. Test desktop GUI: python -m streamlit run desktop_app/app.py")
            print("2. Configure API keys in the GUI Settings panel")
            print("3. Build executable (optional): run build_exe.bat")
            print()
            print("📖 See USER_GUIDE.md for detailed instructions")
            
        except Exception as e:
            print(f"❌ Error during organization: {e}")
            return False
        
        return True

def main():
    """Main function"""
    organizer = ProjectOrganizer()
    success = organizer.run_organization()
    
    if success:
        print("\n🎊 TradeMasterX 2.0 is ready for deployment! 🎊")
    else:
        print("\n💥 Organization failed. Please check errors above.")

if __name__ == "__main__":
    main()
