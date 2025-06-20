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
            if not list(dir_path.glob("*.json")):
                print(f"  └── (no flows yet)")
        else:
            print(f"\n{description}")
            print(f"  └── (directory not found)")

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

def check_database():
    """Check Langflow database location and status"""
    print("🗄️  Langflow Database Information:")
    print("=" * 40)
    
    # Check for database in virtual environment
    venv_db = Path(".venv/lib/python3.10/site-packages/langflow/langflow.db")
    if venv_db.exists():
        print(f"✅ Default database found: {venv_db}")
        stat = venv_db.stat()
        print(f"   Size: {stat.st_size} bytes")
        print(f"   Modified: {datetime.fromtimestamp(stat.st_mtime)}")
    else:
        print("❌ Default database not found")
    
    # Check for custom database
    custom_db = Path("flows/langflow.db")
    if custom_db.exists():
        print(f"✅ Custom database found: {custom_db}")
        stat = custom_db.stat()
        print(f"   Size: {stat.st_size} bytes")
        print(f"   Modified: {datetime.fromtimestamp(stat.st_mtime)}")
    else:
        print("ℹ️  No custom database found")
    
    print("\n💡 Tip: Always export flows to JSON for version control!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/manage_flows.py [list|backup|validate|db]")
        print("\nCommands:")
        print("  list     - List all flows in organized directories")
        print("  backup   - Backup all flows with timestamp")
        print("  validate - Validate a specific flow JSON file")
        print("  db       - Check database location and status")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_flows()
    elif command == "backup":
        backup_flows()
    elif command == "db":
        check_database()
    elif command == "validate":
        if len(sys.argv) < 3:
            print("Usage: python scripts/manage_flows.py validate <flow_file>")
            sys.exit(1)
        
        flow_path = sys.argv[2]
        is_valid, message = validate_flow(flow_path)
        print(f"{'✅' if is_valid else '❌'} {message}")
    else:
        print(f"Unknown command: {command}")
        print("Available commands: list, backup, validate, db") 