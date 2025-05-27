#!/usr/bin/env python3
"""Diagnose the Load Failed error"""

import subprocess
import json
from datetime import datetime

def diagnose_load_failed():
    print("🔍 DIAGNOSING 'LOAD FAILED' ERROR")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check recent commits
    print("\n📝 Recent Changes:")
    result = subprocess.run(
        ["git", "log", "--oneline", "-3", "--format=%h %s (%cr)"],
        capture_output=True, text=True
    )
    print(result.stdout)
    
    print("\n🔍 Common Causes of 'Load Failed':")
    print("\n1. **Import Errors**")
    print("   - Missing dependencies")
    print("   - Circular imports")
    print("   - Module not found errors")
    
    print("\n2. **Configuration Issues**")
    print("   - Invalid langgraph.json")
    print("   - Graph import paths incorrect")
    print("   - Missing required files")
    
    print("\n3. **Code Errors**")
    print("   - Syntax errors in Python files")
    print("   - Runtime errors during graph initialization")
    print("   - Missing environment variables")
    
    # Check for syntax errors
    print("\n🐍 Checking Python Syntax...")
    files_to_check = [
        "eaia/main/graph.py",
        "eaia/cron_graph.py",
        "eaia/reflection_graphs.py",
        "api_config.py",
        "eaia/main/__init__.py",
        "eaia/__init__.py"
    ]
    
    syntax_errors = 0
    for file in files_to_check:
        try:
            result = subprocess.run(
                ["python3", "-m", "py_compile", file],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"   ❌ Syntax error in {file}")
                print(f"      {result.stderr}")
                syntax_errors += 1
            else:
                print(f"   ✅ {file}")
        except Exception as e:
            print(f"   ⚠️  Could not check {file}: {e}")
    
    # Check imports
    print("\n📦 Checking Critical Imports...")
    test_imports = [
        "from eaia.main.graph import graph",
        "from eaia.cron_graph import graph",
        "from eaia.reflection_graphs import general_reflection_graph",
        "from api_config import app"
    ]
    
    for imp in test_imports:
        try:
            result = subprocess.run(
                ["python3", "-c", imp],
                capture_output=True, text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"   ✅ {imp}")
            else:
                print(f"   ❌ {imp}")
                print(f"      Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"   ❌ {imp} - {str(e)}")
    
    # Check langgraph.json
    print("\n📋 Checking langgraph.json...")
    try:
        with open("langgraph.json", "r") as f:
            config = json.load(f)
            print("   ✅ Valid JSON")
            
            # Check graph paths
            for name, path in config.get("graphs", {}).items():
                print(f"   Graph: {name} -> {path}")
                # Extract file and object
                if ":" in path:
                    file_path, obj_name = path.split(":", 1)
                    file_path = file_path.replace("./", "")
                    print(f"      Checking {file_path}...")
                    
                    # Check if file exists
                    import os
                    if os.path.exists(file_path):
                        print(f"      ✅ File exists")
                    else:
                        print(f"      ❌ File not found!")
    except Exception as e:
        print(f"   ❌ Error reading langgraph.json: {e}")
    
    print("\n🔧 IMMEDIATE FIXES TO TRY:")
    print("\n1. **Check deployment logs** (most important):")
    print("   - Go to LangSmith deployment page")
    print("   - Look for the specific error message")
    print("   - It will show the exact import/load error")
    
    print("\n2. **Test locally**:")
    print("   python3 -c \"from eaia.main.graph import graph\"")
    print("   python3 -c \"from api_config import app\"")
    
    print("\n3. **Common fixes**:")
    print("   - Ensure all __init__.py files exist")
    print("   - Check for circular imports")
    print("   - Verify all dependencies are in pyproject.toml")
    
    print("\n4. **If API config is the issue**:")
    print("   - Remove api section from langgraph.json")
    print("   - Or ensure api_config.py is properly configured")

if __name__ == "__main__":
    diagnose_load_failed()