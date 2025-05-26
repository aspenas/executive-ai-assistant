#!/usr/bin/env python3
"""Simple email fetching script using AWS Secrets Manager."""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from eaia.gmail import fetch_group_emails  # noqa: E402
from eaia.main.config import get_config  # noqa: E402


def main():
    """Fetch and display emails."""
    parser = argparse.ArgumentParser(
        description="Fetch emails using AWS Secrets Manager"
    )
    parser.add_argument(
        "--minutes-since",
        type=int,
        default=120,
        help="Fetch emails from the last N minutes (default: 120)"
    )
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="Email address to fetch (default: from config)"
    )
    
    args = parser.parse_args()
    
    # Set AWS environment
    os.environ["USE_AWS_SECRETS"] = "true"
    os.environ["AWS_REGION"] = "us-west-2"
    
    # Get email address
    if args.email:
        email_address = args.email
    else:
        config = get_config({"configurable": {}})
        email_address = config["email"]
    
    print(f"Fetching emails for: {email_address}")
    print(f"From the last {args.minutes_since} minutes")
    print("=" * 70)
    
    count = 0
    responded_count = 0
    
    try:
        for email_data in fetch_group_emails(
            email_address,
            minutes_since=args.minutes_since
        ):
            count += 1
            
            if "user_respond" in email_data:
                responded_count += 1
                print(f"\n[{count}] ✅ Already responded")
                print(f"     Thread ID: {email_data['thread_id']}")
            else:
                print(f"\n[{count}] 📧 New Email")
                print(f"     From: {email_data.get('from_email', 'Unknown')}")
                subject = email_data.get('subject', 'No subject')
                print(f"     Subject: {subject}")
                print(f"     Time: {email_data.get('send_time', 'Unknown')}")
                print(f"     Thread ID: {email_data['thread_id']}")
                
                # Show preview
                content = email_data.get('page_content', '')
                if content:
                    lines = content.strip().split('\n')
                    preview = ' '.join(lines[:3])[:150]
                    if len(preview) == 150 or len(lines) > 3:
                        preview += "..."
                    print(f"     Preview: {preview}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 70)
    print(f"Summary:")
    print(f"  Total emails found: {count}")
    print(f"  Already responded: {responded_count}")
    print(f"  Need attention: {count - responded_count}")
    
    if count == 0:
        print("\nℹ️  No emails found in the specified time range.")
        print("   Try increasing --minutes-since to search further back.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 