# GPT Researcher MCP Server Deployment System

This directory contains automated build and deployment scripts for the GPT Researcher MCP Server.

## 📁 Files Overview

### Core Scripts
- **`build_mcp_streaming.py`** - Builds the MCP server executable using PyInstaller
- **`deploy_mcp_server.py`** - Deploys executable to network share with version control
- **`gpt_researcher_mcp_streaming.py`** - Main MCP server source code

### Batch Files (Windows)
- **`build_and_deploy.bat`** - Complete build and deployment pipeline
- **`deploy_only.bat`** - Deploy existing executable without rebuilding

### Configuration
- **`dataagent_mcp_config_streaming.json`** - Example MCP configuration file

## 🚀 Quick Start

### Option 1: Build and Deploy (Recommended)
```batch
# Double-click or run in command prompt
build_and_deploy.bat
```

### Option 2: Deploy Only (if executable already exists)
```batch
# Double-click or run in command prompt
deploy_only.bat
```

### Option 3: Manual Commands
```batch
# Build only
C:\Users\ianimash\source\repos\venvs\gpt-researcher\Scripts\python.exe build_mcp_streaming.py

# Deploy only
C:\Users\ianimash\source\repos\venvs\gpt-researcher\Scripts\python.exe deploy_mcp_server.py
```

## 📋 What the Deployment System Does

### 🔧 Build Process (`build_mcp_streaming.py`)
1. Installs required dependencies (pyinstaller, mcp)
2. Cleans previous build artifacts
3. Compiles Python source to standalone executable (~112 MB)
4. Creates example MCP configuration file
5. Tests the executable

### 🚀 Deployment Process (`deploy_mcp_server.py`)
1. **Version Control**
   - Automatically increments version number (semantic versioning)
   - Tracks build numbers
   - Maintains deployment history

2. **Backup Management**
   - Creates timestamped backups of previous versions
   - Keeps only the 5 most recent backups
   - Prevents data loss during deployment

3. **Network Deployment**
   - Copies executable to `\\IREGPT1\mcp-servers\`
   - Verifies file integrity after copy
   - Updates configuration examples

4. **Logging & Tracking**
   - Comprehensive deployment logging
   - Tracks who deployed when and from which machine
   - Maintains version history with metadata

## 📊 Version Control System

The deployment system maintains a `version.json` file on the network share:

```json
{
  "version": "1.0.3",
  "build": 15,
  "deployments": [
    {
      "version": "1.0.3",
      "build": 15,
      "timestamp": "2025-09-18T02:30:45.123456",
      "deployed_by": "ianimash",
      "machine": "DESKTOP-XYZ",
      "executable_size": 117440512,
      "local_path": "C:\\Users\\ianimash\\source\\repos\\gpt-researcher\\dist\\gpt-researcher-mcp-streaming.exe",
      "network_path": "\\\\IREGPT1\\mcp-servers\\gpt-researcher-mcp-streaming.exe"
    }
  ]
}
```

## 📁 File Locations

### Local Development
- **Source**: `c:\Users\ianimash\source\repos\gpt-researcher\`
- **Executable**: `c:\Users\ianimash\source\repos\gpt-researcher\dist\gpt-researcher-mcp-streaming.exe`
- **Config**: `c:\Users\ianimash\source\repos\gpt-researcher\dataagent_mcp_config_streaming.json`

### Network Share
- **Location**: `\\IREGPT1\mcp-servers\`
- **Executable**: `\\IREGPT1\mcp-servers\gpt-researcher-mcp-streaming.exe`
- **Version Info**: `\\IREGPT1\mcp-servers\version.json`
- **Config Example**: `\\IREGPT1\mcp-servers\dataagent_mcp_config_streaming.json`
- **Deployment Log**: `\\IREGPT1\mcp-servers\deployment.log`
- **Backups**: `\\IREGPT1\mcp-servers\gpt-researcher-mcp-streaming.exe.backup_YYYYMMDD_HHMMSS`

## 🔧 DataAgent Configuration

After deployment, configure DataAgent to use the MCP server:

1. **Copy the configuration**:
   ```
   From: \\IREGPT1\mcp-servers\dataagent_mcp_config_streaming.json
   To:   %APPDATA%\DataAgent\dataagent_mcp_config.json
   ```

2. **Restart DataAgent** to load the new MCP server

3. **Verify** the server appears in DataAgent's MCP tools list

## 🛠️ Troubleshooting

### Common Issues

1. **"Access Denied" to network share**
   - Ensure you have write permissions to `\\IREGPT1\mcp-servers\`
   - Try running as administrator

2. **"Build failed" error**
   - Check if the virtual environment exists
   - Verify Python dependencies are installed
   - Look for specific error messages in build output

3. **"Executable not found" error**
   - Run `build_and_deploy.bat` instead of `deploy_only.bat`
   - Check if the build completed successfully

4. **Network share not accessible**
   - Verify network connectivity
   - Check if `\\IREGPT1\mcp-servers\` is accessible
   - Ensure proper permissions

### Debug Information

The deployment script provides detailed logging:
- Real-time console output
- Network share deployment log
- Version history tracking
- File size verification

## 🔍 Features

### ✅ What It Does
- ✅ Automatic version incrementing
- ✅ Backup management (keeps 5 recent versions)
- ✅ Network share deployment
- ✅ Local copy preservation for testing
- ✅ Comprehensive logging and tracking
- ✅ Configuration file management
- ✅ File integrity verification
- ✅ Deployment history

### 📋 Benefits
- **Version Control**: Never lose track of what version is deployed
- **Rollback Capability**: Easy access to previous versions via backups
- **Audit Trail**: Complete deployment history with timestamps and metadata
- **Safety**: Preserves local copies for continued development/testing
- **Automation**: One-click build and deployment process
- **Reliability**: File integrity checks and error handling

## 📝 Example Usage

```batch
# Complete build and deployment
> build_and_deploy.bat

🚀 GPT Researcher MCP Server - Build and Deploy
==================================================

Step 1: Building MCP Server executable...
------------------------------------------
✅ Build completed successfully!
📊 File size: 111.9 MB

Step 2: Deploying to network share...
------------------------------------
🚀 Starting GPT Researcher MCP Server deployment...
✅ Found executable: dist\gpt-researcher-mcp-streaming.exe (111.9 MB)
✅ Network share accessible: \\IREGPT1\mcp-servers
📋 Current version: v1.0.2 (build 14)
📋 Version incremented: v1.0.3 (build 15)
✅ Created backup: gpt-researcher-mcp-streaming.exe.backup_20250918_023045
✅ Executable deployed successfully
✅ Version file updated: v1.0.3 (build 15)
✅ Updated MCP config example

============================================
   Build and Deployment completed successfully!
============================================
```

This deployment system ensures reliable, versioned deployments while maintaining local development capabilities.