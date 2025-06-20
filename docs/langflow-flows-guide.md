# 🔄 Langflow Flows Management Guide

## 📍 Where Langflow Flows Are Saved

### Default Storage Location
Langflow stores flows in a **SQLite database** by default:
```
.venv/lib/python3.10/site-packages/langflow/langflow.db
```

**⚠️ Important**: This location is inside your virtual environment and **should NOT be committed to git**.

### Recommended Flow Management Strategy

#### 1. **Export Flows to Version Control**
Always export your flows as JSON files for version control:

```bash
# Create flows directory (already exists)
mkdir -p flows/

# Export flows from Langflow UI:
# 1. Open flow in Langflow
# 2. Click "Export" button 
# 3. Save to flows/ directory
```

#### 2. **Organized Flow Structure**
```
flows/
├── voice-commands/
│   ├── voice-command-processor.json
│   └── voice-command-processor-v2.json
├── attendee-qa/
│   ├── faq-bot.json
│   └── faq-bot-advanced.json
├── escalation/
│   ├── smart-escalation.json
│   └── escalation-rules.json
└── demo/
    ├── demo-controller.json
    └── demo-scenarios.json
```

## 🎯 eMCeeP Flow Organization

### Phase 1 Core Flows

#### **1. Voice Command Processor**
- **File**: `flows/voice-commands/voice-command-processor.json`
- **Purpose**: Process organizer voice commands
- **Components**: 
  - Text Input (voice simulation)
  - Intent Classifier (Python function)
  - Mistral LLM
  - Event Data Updater
  - SMS Notifier

#### **2. FAQ Bot**
- **File**: `flows/attendee-qa/faq-bot.json`
- **Purpose**: Answer attendee questions instantly
- **Components**:
  - Text Input (attendee question)
  - FAQ Matcher (Python function)
  - Mistral LLM (contextual answers)
  - Response Formatter

#### **3. Smart Escalation**
- **File**: `flows/escalation/smart-escalation.json`
- **Purpose**: Detect when organizer intervention needed
- **Components**:
  - Question Analyzer
  - Escalation Logic (Python function)
  - Alert Sender (Twilio)

## 🔧 Flow Management Commands

### Starting Langflow with Proper Configuration
```bash
# Navigate to project directory
cd /path/to/langflow-hackathon-june-20-2025

# Activate virtual environment
source .venv/bin/activate

# Start Langflow with project-specific settings
langflow run --host 0.0.0.0 --port 7860 --env-file .env

# Alternative: Start with custom database location
LANGFLOW_DATABASE_URL="sqlite:///./flows/langflow.db" langflow run
```

### Exporting Flows (Manual Process)
1. **Open Langflow UI**: http://localhost:7860
2. **Select Flow**: Click on the flow you want to export
3. **Export**: Click the "Export" button (download icon)
4. **Save**: Save to appropriate `flows/` subdirectory
5. **Commit**: Add to git version control

### Importing Flows
1. **Open Langflow UI**: http://localhost:7860
2. **Import**: Click "Import" or "Upload" button
3. **Select File**: Choose JSON file from `flows/` directory
4. **Edit/Test**: Modify as needed
5. **Re-export**: Save changes back to JSON

## 📦 Backup and Version Control Strategy

### What to Commit to Git
```bash
# ✅ DO commit these
flows/                    # Exported flow JSON files
scripts/                  # Helper scripts
data/                     # Demo data
docs/                     # Documentation
requirements.txt          # Dependencies
.env.template             # Environment template

# ❌ DON'T commit these
.env                      # Contains secrets
.venv/                    # Virtual environment
*.db                      # Database files
logs/                     # Log files
__pycache__/             # Python cache
```

### Automated Export Script
Let's create a helper script for flow management:

```python
# scripts/manage_flows.py
#!/usr/bin/env python3
"""
Flow management helper for eMCeeP project
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

def backup_flows():
    """Backup current flows with timestamp"""
    backup_dir = Path("flows/backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Copy all flow files to backup
    for flow_file in Path("flows").glob("**/*.json"):
        if "backups" not in str(flow_file):
            backup_path = backup_dir / f"{flow_file.stem}_{timestamp}.json"
            shutil.copy2(flow_file, backup_path)
            print(f"Backed up: {flow_file} -> {backup_path}")

def list_flows():
    """List all available flows"""
    print("📋 Available eMCeeP Flows:")
    print("=" * 40)
    
    flow_dirs = {
        "voice-commands": "🎤 Voice Command Processing",
        "attendee-qa": "❓ Attendee Q&A System", 
        "escalation": "🚨 Smart Escalation",
        "demo": "🎬 Demo Controllers"
    }
    
    for dir_name, description in flow_dirs.items():
        dir_path = Path("flows") / dir_name
        if dir_path.exists():
            print(f"\n{description}")
            for flow_file in dir_path.glob("*.json"):
                print(f"  └── {flow_file.name}")
        else:
            print(f"\n{description}")
            print(f"  └── (no flows yet)")

def validate_flow(flow_path):
    """Validate a flow JSON file"""
    try:
        with open(flow_path) as f:
            flow_data = json.load(f)
        
        # Basic validation
        required_fields = ["data", "nodes", "edges"]
        for field in required_fields:
            if field not in flow_data:
                return False, f"Missing required field: {field}"
        
        return True, "Flow is valid"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error: {e}"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/manage_flows.py [list|backup|validate]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_flows()
    elif command == "backup":
        backup_flows()
    elif command == "validate":
        if len(sys.argv) < 3:
            print("Usage: python scripts/manage_flows.py validate <flow_file>")
            sys.exit(1)
        
        flow_path = sys.argv[2]
        is_valid, message = validate_flow(flow_path)
        print(f"{'✅' if is_valid else '❌'} {message}")
    else:
        print(f"Unknown command: {command}")
```

## 🎬 Demo Flow Workflow

### Development Process
1. **Create Flow in UI**
   - Design components in Langflow interface
   - Test with sample data
   - Verify connections work

2. **Export for Version Control**
   ```bash
   # Save to appropriate directory
   flows/voice-commands/voice-command-processor.json
   ```

3. **Commit to Git**
   ```bash
   git add flows/voice-commands/voice-command-processor.json
   git commit -m "Add voice command processor flow"
   ```

4. **Share with Team**
   ```bash
   git push origin andrea
   ```

### Demo Day Preparation
```bash
# 1. Start fresh Langflow instance
langflow run --host 0.0.0.0 --port 7860

# 2. Import all demo flows
# (via UI or programmatically)

# 3. Test each flow
python scripts/test_flows.py

# 4. Backup before demo
python scripts/manage_flows.py backup
```

## 🚨 Troubleshooting

### Common Issues

#### **Flow Not Saving**
- Check Langflow logs: `tail -f langflow.log`
- Verify database permissions
- Restart Langflow if needed

#### **Lost Flows**
- Check backup directory: `flows/backups/`
- Look for auto-saves in browser downloads
- Recreate from git history if available

#### **Import Errors**
- Validate JSON: `python scripts/manage_flows.py validate flows/file.json`
- Check Langflow version compatibility
- Verify all components are available

### Recovery Commands
```bash
# Find database location
find . -name "*.db" -path "*langflow*"

# Copy database for backup
cp .venv/lib/python3.10/site-packages/langflow/langflow.db ./flows/backup.db

# Reset database (DANGER - will lose all flows!)
rm .venv/lib/python3.10/site-packages/langflow/langflow.db
```

## 📝 Best Practices

### 1. **Regular Exports**
- Export flows after every major change
- Use descriptive filenames with version numbers
- Commit to git frequently

### 2. **Flow Naming Convention**
```
{purpose}-{version}.json

Examples:
voice-command-processor-v1.json
faq-bot-basic.json
escalation-advanced-v2.json
demo-controller-final.json
```

### 3. **Documentation in Flows**
- Add descriptions to components
- Use meaningful node names
- Include comments in Python functions

### 4. **Testing Strategy**
- Test each flow individually
- Validate with real API calls
- Create test data for each scenario

---

**Remember**: Langflow flows are stored in a database by default, but for the eMCeeP hackathon project, always export important flows to JSON files in the `flows/` directory for version control and sharing! 🎤✨ 