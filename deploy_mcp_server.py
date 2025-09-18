#!/usr/bin/env python3
"""
GPT Researcher MCP Server Deployment Script
============================================

This script deploys the compiled MCP server executable to the network share
with automatic version control and maintains local copies for testing.

Features:
- Automatic version incrementing
- Network share deployment
- Local copy preservation
- Backup management
- Deployment logging
"""

import os
import shutil
import json
import datetime
from pathlib import Path
import subprocess
import sys

# Configuration
NETWORK_SHARE = r"\\IREGPT1\mcp-servers\gpt-researcher"
LOCAL_DIST_DIR = Path(__file__).parent / "dist"
EXECUTABLE_NAME = "gpt-researcher-mcp-streaming.exe"
VERSION_FILE = "version.json"
DEPLOYMENT_LOG = "deployment.log"

class DeploymentManager:
    def __init__(self):
        self.network_path = Path(NETWORK_SHARE)
        self.local_dist = LOCAL_DIST_DIR
        self.executable_path = self.local_dist / EXECUTABLE_NAME
        self.version_file_path = self.network_path / VERSION_FILE
        self.log_file_path = self.network_path / DEPLOYMENT_LOG
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        # Also log to file if network share is accessible
        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass  # Silently continue if logging to network fails
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met for deployment"""
        self.log("Checking deployment prerequisites...")
        
        # Check if executable exists
        if not self.executable_path.exists():
            self.log(f"ERROR: Executable not found at {self.executable_path}", "ERROR")
            self.log("Please run build_mcp_streaming.py first to create the executable", "ERROR")
            return False
        
        executable_size = self.executable_path.stat().st_size / (1024 * 1024)  # MB
        self.log(f"Found executable: {self.executable_path} ({executable_size:.1f} MB)")
        
        # Check network share accessibility and create directory if needed
        try:
            if not self.network_path.exists():
                self.log(f"Creating network directory: {self.network_path}")
                self.network_path.mkdir(parents=True, exist_ok=True)
            
            self.log(f"Network share accessible: {self.network_path}")
        except Exception as e:
            self.log(f"ERROR: Cannot access or create network share: {self.network_path} - {e}", "ERROR")
            self.log("Please ensure you have write permissions to the network share", "ERROR")
            return False
        return True
    
    def get_current_version(self) -> dict:
        """Get the current version information from network share"""
        try:
            if self.version_file_path.exists():
                with open(self.version_file_path, "r", encoding="utf-8") as f:
                    version_data = json.load(f)
                self.log(f"Current version: v{version_data['version']} (build {version_data['build']})")
                return version_data
            else:
                self.log("No version file found, starting with v1.0.0")
                return {
                    "version": "1.0.0",
                    "build": 0,
                    "deployments": []
                }
        except Exception as e:
            self.log(f"Error reading version file: {e}", "ERROR")
            return {
                "version": "1.0.0", 
                "build": 0,
                "deployments": []
            }
    
    def increment_version(self, version_data: dict) -> dict:
        """Increment the version number"""
        current_version = version_data["version"]
        current_build = version_data.get("build", 0)
        
        # Parse version (assuming semantic versioning)
        try:
            major, minor, patch = map(int, current_version.split("."))
        except ValueError:
            major, minor, patch = 1, 0, 0
        
        # Increment patch version and build number
        patch += 1
        current_build += 1
        
        new_version = f"{major}.{minor}.{patch}"
        
        version_data["version"] = new_version
        version_data["build"] = current_build
        
        self.log(f"Version incremented: v{new_version} (build {current_build})")
        return version_data
    
    def create_backup(self) -> bool:
        """Create backup of existing executable on network share"""
        network_executable = self.network_path / EXECUTABLE_NAME
        
        if network_executable.exists():
            # Create backup with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{EXECUTABLE_NAME}.backup_{timestamp}"
            backup_path = self.network_path / backup_name
            
            try:
                shutil.copy2(network_executable, backup_path)
                self.log(f"Created backup: {backup_name}")
                
                # Clean up old backups (keep only last 5)
                self.cleanup_old_backups()
                return True
                
            except Exception as e:
                self.log(f"Failed to create backup: {e}", "ERROR")
                return False
        else:
            self.log("No existing executable to backup")
            return True
    
    def cleanup_old_backups(self):
        """Keep only the 5 most recent backups"""
        try:
            backup_files = list(self.network_path.glob(f"{EXECUTABLE_NAME}.backup_*"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups (keep only 5 most recent)
            for old_backup in backup_files[5:]:
                old_backup.unlink()
                self.log(f"Removed old backup: {old_backup.name}")
                
        except Exception as e:
            self.log(f"Error cleaning up backups: {e}", "WARNING")
    
    def deploy_executable(self) -> bool:
        """Deploy the executable to network share"""
        network_executable = self.network_path / EXECUTABLE_NAME
        
        try:
            # Copy executable to network share
            shutil.copy2(self.executable_path, network_executable)
            
            # Verify the copy
            local_size = self.executable_path.stat().st_size
            network_size = network_executable.stat().st_size
            
            if local_size != network_size:
                self.log(f"Size mismatch: local={local_size}, network={network_size}", "ERROR")
                return False
            
            self.log(f"Executable deployed successfully: {network_executable}")
            return True
            
        except Exception as e:
            self.log(f"Failed to deploy executable: {e}", "ERROR")
            return False
    
    def update_version_file(self, version_data: dict) -> bool:
        """Update the version file with new deployment information"""
        try:
            # Add deployment record
            deployment_record = {
                "version": version_data["version"],
                "build": version_data["build"],
                "timestamp": datetime.datetime.now().isoformat(),
                "deployed_by": os.getenv("USERNAME", "unknown"),
                "machine": os.getenv("COMPUTERNAME", "unknown"),
                "executable_size": self.executable_path.stat().st_size,
                "local_path": str(self.executable_path),
                "network_path": str(self.network_path / EXECUTABLE_NAME)
            }
            
            version_data["deployments"].append(deployment_record)
            
            # Keep only last 10 deployment records
            version_data["deployments"] = version_data["deployments"][-10:]
            
            # Write updated version file
            with open(self.version_file_path, "w", encoding="utf-8") as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
            
            self.log(f"Version file updated: v{version_data['version']} (build {version_data['build']})")
            return True
            
        except Exception as e:
            self.log(f"Failed to update version file: {e}", "ERROR")
            return False
    
    def create_config_example(self) -> bool:
        """Create/update MCP configuration example on network share"""
        try:
            local_config = Path(__file__).parent / "dataagent_mcp_config_streaming.json"
            network_config = self.network_path / "dataagent_mcp_config_streaming.json"
            
            if local_config.exists():
                # Update the config to point to network path
                with open(local_config, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                
                # Update the executable path to network location
                if "mcpServers" in config_data:
                    for server_name, server_config in config_data["mcpServers"].items():
                        if "command" in server_config:
                            server_config["command"] = str(self.network_path / EXECUTABLE_NAME)
                
                # Write updated config to network share
                with open(network_config, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=2)
                
                self.log(f"Updated MCP config example: {network_config}")
                return True
            else:
                self.log("No local config file found to copy", "WARNING")
                return True
                
        except Exception as e:
            self.log(f"Failed to create config example: {e}", "ERROR")
            return False
    
    def display_deployment_summary(self, version_data: dict):
        """Display a summary of the deployment"""
        print("\n" + "="*60)
        print("🚀 DEPLOYMENT SUMMARY")
        print("="*60)
        print(f"📋 Version: v{version_data['version']} (build {version_data['build']})")
        print(f"📁 Local Executable: {self.executable_path}")
        print(f"🌐 Network Location: {self.network_path / EXECUTABLE_NAME}")
        print(f"📊 File Size: {self.executable_path.stat().st_size / (1024*1024):.1f} MB")
        print(f"🕐 Deployed At: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👤 Deployed By: {os.getenv('USERNAME', 'unknown')}")
        print(f"💻 Machine: {os.getenv('COMPUTERNAME', 'unknown')}")
        print("\n📋 Next Steps:")
        print(f"1. Copy the config from: {self.network_path}/dataagent_mcp_config_streaming.json")
        print(f"2. Place it in: %APPDATA%\\DataAgent\\dataagent_mcp_config.json")
        print(f"3. Restart DataAgent to load the new version")
        print("="*60)
    
    def deploy(self) -> bool:
        """Main deployment function"""
        self.log("🚀 Starting GPT Researcher MCP Server deployment...")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Get current version
        version_data = self.get_current_version()
        
        # Increment version
        version_data = self.increment_version(version_data)
        
        # Create backup
        if not self.create_backup():
            self.log("Backup creation failed, but continuing with deployment...", "WARNING")
        
        # Deploy executable
        if not self.deploy_executable():
            return False
        
        # Update version file
        if not self.update_version_file(version_data):
            self.log("Version file update failed, but deployment was successful", "WARNING")
        
        # Create config example
        if not self.create_config_example():
            self.log("Config example creation failed, but deployment was successful", "WARNING")
        
        # Display summary
        self.display_deployment_summary(version_data)
        
        self.log("✅ Deployment completed successfully!")
        return True

def main():
    """Main function"""
    print("🚀 GPT Researcher MCP Server Deployment Tool")
    print("=" * 50)
    
    # Check if running as admin (recommended for network operations)
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("⚠️  Warning: Not running as administrator. Network operations may fail.")
    except Exception:
        pass
    
    # Create deployment manager and deploy
    deployer = DeploymentManager()
    
    try:
        success = deployer.deploy()
        if success:
            print("\n🎉 Deployment successful!")
            sys.exit(0)
        else:
            print("\n❌ Deployment failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()