#!/usr/bin/env python3
"""
Dynamic Art Generator Setup Script
Automatically checks dependencies and helps with installation

Author: Claude Assistant
Version: 1.0
"""

import sys
import subprocess
import platform
import importlib
import os

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is not installed")
        return False

def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package_name}")
        return False

def check_system_dependencies():
    """Check platform-specific dependencies"""
    system = platform.system().lower()
    print(f"\n🔍 Checking system dependencies for {system}...")
    
    if system == "linux":
        print("📋 For Linux users:")
        print("   Run: sudo apt-get install portaudio19-dev python3-dev")
        print("   This is required for audio functionality")
    elif system == "darwin":  # macOS
        print("📋 For macOS users:")
        print("   Run: brew install portaudio")
        print("   This is required for audio functionality")
    elif system == "windows":
        print("📋 For Windows users:")
        print("   You may need Microsoft Visual C++ Build Tools")
        print("   Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/")

def main():
    """Main setup function"""
    print("🎨 Dynamic Art Generator Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    print("\n🔍 Checking dependencies...")
    
    # Required packages
    packages = [
        ("pygame", "pygame"),
        ("numpy", "numpy"),
        ("pillow", "PIL"),
        ("pyaudio", "pyaudio"),
        ("librosa", "librosa"),
        ("soundfile", "soundfile"),
        ("scipy", "scipy"),
        ("matplotlib", "matplotlib")
    ]
    
    missing_packages = []
    
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            missing_packages.append(package_name)
    
    # Check system dependencies
    check_system_dependencies()
    
    # Install missing packages
    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing packages...")
        
        for package in missing_packages:
            print(f"\n⬇️ Installing {package}...")
            if not install_package(package):
                print(f"⚠️ Manual installation may be required for {package}")
    else:
        print("\n✅ All required packages are installed!")
    
    # Create project structure
    print("\n📁 Setting up project structure...")
    
    directories = [
        "plugins",
        "utils", 
        "presets",
        "examples",
        "logs"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📂 Directory exists: {directory}")
    
    # Create __init__.py files
    init_files = [
        "plugins/__init__.py",
        "utils/__init__.py"
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Package initialization file\n')
            print(f"✅ Created: {init_file}")
    
    # Test audio functionality
    print("\n🎵 Testing audio functionality...")
    try:
        import pyaudio
        import librosa
        
        # Quick test of pyaudio
        audio = pyaudio.PyAudio()
        device_count = audio.get_device_count()
        audio.terminate()
        
        print(f"✅ Audio system working! Found {device_count} audio devices")
        
        # Test librosa
        sr = librosa.get_samplerate("dummy_nonexistent_file.wav", default=44100)
        print("✅ Librosa working!")
        
    except Exception as e:
        print(f"⚠️ Audio test failed: {e}")
        print("   Audio functionality may be limited")
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\n📋 Next steps:")
    print("1. Run: python main.py")
    print("2. Select an art plugin from the dropdown")
    print("3. Enable audio input and click 'Start'")
    print("4. Make some noise and watch the art respond!")
    
    print("\n💡 Tips:")
    print("- Adjust plugin parameters with the sliders")
    print("- Try different audio sources (microphone, music)")
    print("- Use 'Reset' to clear the canvas")
    
    print("\n🔧 Troubleshooting:")
    print("- If audio doesn't work, check microphone permissions")
    print("- For performance issues, reduce particle counts")
    print("- Check the console for error messages")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✨ Ready to create some dynamic art!")
        else:
            print("\n❌ Setup incomplete. Please check the errors above.")
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup interrupted by user")
    except Exception as e:
        print(f"\n💥 Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
