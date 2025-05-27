#!/usr/bin/env python3
"""Fix model configuration issue"""

import os

# Files that need fixing
files_to_fix = [
    "eaia/main/find_meeting_time.py",
    "eaia/main/triage.py", 
    "eaia/main/rewrite.py"
]

def fix_model_config():
    print("🔧 Fixing model configuration issue...")
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix the model configuration line
        old_line = 'model = config["configurable"].get("model", "gpt-4o")'
        new_line = 'model = config.get("configurable", {}).get("model") or "gpt-4o"'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
        else:
            print(f"⚠️  Pattern not found in: {file_path}")
            # Try alternative fix
            if 'config["configurable"].get("model"' in content:
                content = content.replace(
                    'config["configurable"].get("model"',
                    'config.get("configurable", {}).get("model"'
                )
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"✅ Fixed (alternative): {file_path}")
    
    print("\n📝 Creating updated config.yaml with model specification...")
    
    # Add model to config.yaml
    with open("eaia/main/config.yaml", 'r') as f:
        config_content = f.read()
    
    if "model:" not in config_content:
        # Add model configuration after the email line
        lines = config_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('email:'):
                lines.insert(i + 1, '')
                lines.insert(i + 2, '# Default AI model to use')
                lines.insert(i + 3, 'model: gpt-4o')
                break
        
        with open("eaia/main/config.yaml", 'w') as f:
            f.write('\n'.join(lines))
        print("✅ Added model configuration to config.yaml")
    
    print("\n✅ Model configuration fixed!")
    print("\n🚀 Next steps:")
    print("1. Commit and push these changes")
    print("2. Trigger a new deployment")
    print("3. Test in LangGraph Studio")

if __name__ == "__main__":
    fix_model_config()