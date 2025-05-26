#!/usr/bin/env python3
"""Test email fetching with AWS Secrets Manager."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eaia.gmail import fetch_group_emails  # noqa: E402


def main():
    """Test email fetching."""
    print("Testing Email Fetch with AWS Secrets Manager")
    print("=" * 50)
    
    # Set environment for AWS
    os.environ["USE_AWS_SECRETS"] = "true"
    os.environ["AWS_REGION"] = "us-west-2"
    
    email = "patrick@highline.work"
    minutes = 120
    
    print(f"Fetching emails for: {email}")
    print(f"From the last: {minutes} minutes")
    print("-" * 50)
    
    try:
        count = 0
        for email_data in fetch_group_emails(email, minutes_since=minutes):
            count += 1
            
            if "user_respond" in email_data:
                print(f"\n📧 Email #{count} (User already responded)")
                print(f"   ID: {email_data['id']}")
                print(f"   Thread ID: {email_data['thread_id']}")
            else:
                print(f"\n📧 Email #{count}")
                print(f"   From: {email_data.get('from_email', 'Unknown')}")
                print(f"   To: {email_data.get('to_email', 'Unknown')}")
                print(f"   Subject: {email_data.get('subject', 'No subject')}")
                print(f"   Time: {email_data.get('send_time', 'Unknown')}")
                print(f"   ID: {email_data['id']}")
                print(f"   Thread ID: {email_data['thread_id']}")
                
                # Show first 100 chars of content
                content = email_data.get('page_content', '')
                if content:
                    preview = content[:100].replace('\n', ' ')
                    if len(content) > 100:
                        preview += "..."
                    print(f"   Preview: {preview}")
        
        print("\n" + "-" * 50)
        print(f"Total emails found: {count}")
        
        if count == 0:
            print("\nNo emails found. This could mean:")
            print("- No new emails in the specified time range")
            print("- All recent emails have already been responded to")
            print("- The email address might not match")
        
    except Exception as e:
        print(f"\n❌ Error fetching emails: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 