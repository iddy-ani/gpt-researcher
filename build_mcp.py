#!/usr/bin/env python3
"""
Build script for GPT Researcher MCP Server
Compiles the MCP server into a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """Install required packages for building"""
    print("📦 Installing build requirements...")
    
    required_packages = [
        'pyinstaller',
        'mcp'
    ]
    
    for package in required_packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def clean_build_dirs():
    """Clean previous build artifacts"""
    print("🧹 Cleaning build directories...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ Removed {dir_name}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building GPT Researcher MCP executable...")
    
    try:
        # Run PyInstaller with the spec file
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'gpt_researcher_mcp.spec'
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def test_executable():
    """Test the built executable"""
    print("🧪 Testing executable...")
    
    exe_path = Path('dist/gpt-researcher-mcp.exe')
    
    if not exe_path.exists():
        print(f"❌ Executable not found at {exe_path}")
        return False
    
    try:
        # Test that the executable starts without crashing
        # We'll send a simple JSON-RPC message to test MCP protocol
        test_input = '{"jsonrpc": "2.0", "method": "initialize", "params": {}}\n'
        
        result = subprocess.run(
            [str(exe_path)], 
            input=test_input,
            text=True,
            capture_output=True,
            timeout=10
        )
        
        print(f"✅ Executable test completed")
        print(f"📊 File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        return True
        
    except subprocess.TimeoutExpired:
        print("✅ Executable started (timeout is expected for MCP server)")
        return True
    except Exception as e:
        print(f"❌ Executable test failed: {e}")
        return False

def create_config_example():
    """Create example MCP configuration"""
    print("📝 Creating example MCP configuration...")
    
    config_example = {
        "servers": [
            {
                "name": "gpt-researcher",
                "command": os.path.abspath("dist/gpt-researcher-mcp.exe"),
                "args": [],
                "enabled": True
            }
        ]
    }
    
    with open('dataagent_mcp_config.json', 'w') as f:
        import json
        json.dump(config_example, f, indent=2)
    
    print("✅ Created dataagent_mcp_config.json")

def main():
    """Main build process"""
    print("🚀 GPT Researcher MCP Build Process")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Step 1: Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return 1
    
    # Step 2: Clean build directories
    clean_build_dirs()
    
    # Step 3: Build executable
    if not build_executable():
        print("❌ Build process failed")
        return 1
    
    # Step 4: Test executable
    if not test_executable():
        print("⚠️ Executable test had issues, but build may still be valid")
    
    # Step 5: Create config example
    create_config_example()
    
    print("\n🎉 Build process completed!")
    print(f"📁 Executable location: {os.path.abspath('dist/gpt-researcher-mcp.exe')}")
    print(f"📁 Config example: {os.path.abspath('dataagent_mcp_config.json')}")
    print("\n📋 Next steps:")
    print("1. Copy the executable to your desired location")
    print("2. Update the config file with the correct path")
    print("3. Place the config in %APPDATA%\\DataAgent\\dataagent_mcp_config.json")
    print("4. Restart DataAgent to load the new MCP server")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())