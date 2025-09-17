#!/usr/bin/env python3
"""
Build script for GPT Researcher MCP Server (Streaming Version)
Creates a standalone executable using PyInstaller
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
import json

def main():
    print("🚀 GPT Researcher MCP Build Process (Streaming Version)")
    print("=" * 50)
    
    try:
        # Ensure we're in the right directory
        script_dir = Path(__file__).parent.absolute()
        os.chdir(script_dir)
        
        # Install requirements
        print("📦 Installing build requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "mcp"], 
                      check=True, capture_output=True)
        print("✅ Installed pyinstaller")
        print("✅ Installed mcp")
        
        # Clean build directories
        print("🧹 Cleaning build directories...")
        for dir_name in ["build", "dist", "__pycache__"]:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)
                print(f"✅ Removed {dir_name}")
        
        # Build executable using simple command
        print("🔨 Building GPT Researcher MCP (Streaming) executable...")
        build_cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", "gpt-researcher-mcp-streaming",
            "--add-data", "gpt_researcher;gpt_researcher",
            "--hidden-import", "gpt_researcher",
            "--hidden-import", "mcp",
            "--hidden-import", "aiohttp",
            "--clean",
            "--noconfirm",
            "gpt_researcher_mcp_streaming.py"
        ]
        
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
        else:
            raise subprocess.CalledProcessError(result.returncode, build_cmd, 
                                               result.stdout, result.stderr)
        
        # Test the executable
        print("🧪 Testing executable...")
        exe_path = Path("dist/gpt-researcher-mcp-streaming.exe")
        if exe_path.exists():
            # Quick test - just make sure it starts
            test_proc = subprocess.Popen([str(exe_path)], 
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE,
                                       text=True)
            test_proc.terminate()
            test_proc.wait()
            print("✅ Executable test completed")
            
            # Get file size
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📊 File size: {size_mb:.1f} MB")
        else:
            print("❌ Executable not found")
            
        # Create MCP configuration for streaming version
        print("📝 Creating example MCP configuration...")
        config = {
            "servers": [
                {
                    "name": "gpt-researcher-streaming",
                    "command": str(exe_path.absolute()).replace('\\', '\\\\'),
                    "args": [],
                    "enabled": True
                }
            ]
        }
        
        config_path = Path("dataagent_mcp_config_streaming.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Created dataagent_mcp_config_streaming.json")
        
        print("\n🎉 Build process completed!")
        print(f"📁 Executable location: {exe_path.absolute()}")
        print(f"📁 Config example: {config_path.absolute()}")
        print(f"\n📋 Next steps:")
        print("1. Copy the executable to your desired location")
        print("2. Update the config file with the correct path")
        print("3. Place the config in %APPDATA%\\DataAgent\\dataagent_mcp_config.json")
        print("4. Restart DataAgent to load the new MCP server")
        print("5. The streaming version provides progress notifications!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
        return 1
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())