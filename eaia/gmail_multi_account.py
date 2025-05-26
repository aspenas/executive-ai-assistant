"""Enhanced Gmail integration with multi-account support via AWS Secrets Manager."""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from eaia.aws_secrets import get_secret, SecretsManager

logger = logging.getLogger(__name__)

# Gmail API scopes
_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]

# Cache for credentials to avoid repeated AWS calls
_CREDENTIALS_CACHE: Dict[str, Credentials] = {}


def get_account_secret_name(email: str) -> str:
    """Get the AWS secret name for a given email account.
    
    Args:
        email: Email address
        
    Returns:
        AWS secret name for the account
    """
    # Handle the two known accounts
    if email == "patrick@highline.work":
        return "eaia/gmail-credentials"
    elif email == "patrick.smith@gmail.com":
        return "eaia/gmail-credentials-patrick-dot-smith-at-gmail-dot-com-v2"
    else:
        # Generic pattern for other accounts
        safe_email = email.replace('@', '-at-').replace('.', '-dot-')
        return f"eaia/gmail-credentials-{safe_email}"


def get_credentials_for_account(email: str, force_refresh: bool = False) -> Credentials:
    """Get Gmail credentials for a specific email account from AWS.
    
    Args:
        email: Email address to get credentials for
        force_refresh: Force refresh of credentials even if cached
        
    Returns:
        Google credentials object
        
    Raises:
        ValueError: If credentials not found or invalid
    """
    # Check cache first
    if not force_refresh and email in _CREDENTIALS_CACHE:
        creds = _CREDENTIALS_CACHE[email]
        if creds and creds.valid:
            return creds
    
    # Get from AWS
    secret_name = get_account_secret_name(email)
    
    try:
        secret_data = get_secret(secret_name)
        
        # Extract token data
        gmail_token_str = secret_data.get("gmail_token", "")
        if not gmail_token_str:
            raise ValueError(f"No token found in secret {secret_name}")
        
        # Parse token JSON
        if isinstance(gmail_token_str, str):
            token_data = json.loads(gmail_token_str)
        else:
            token_data = gmail_token_str
        
        # Create credentials object
        creds = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get("token_uri"),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes", _SCOPES),
        )
        
        # Refresh if needed
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                logger.info(f"Refreshing expired credentials for {email}")
                creds.refresh(Request())
                
                # Update the token in AWS
                _update_token_in_aws(email, creds)
            else:
                raise ValueError(f"Invalid credentials for {email} - re-authentication needed")
        
        # Cache the credentials
        _CREDENTIALS_CACHE[email] = creds
        
        logger.info(f"Successfully loaded credentials for {email}")
        return creds
        
    except Exception as e:
        logger.error(f"Failed to get credentials for {email}: {e}")
        raise


def _update_token_in_aws(email: str, creds: Credentials) -> None:
    """Update the token in AWS after refresh.
    
    Args:
        email: Email address
        creds: Updated credentials
    """
    try:
        secret_name = get_account_secret_name(email)
        sm = SecretsManager()
        
        # Get existing secret
        secret_data = sm.get_secret(secret_name)
        
        # Update token data
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes,
            'expiry': creds.expiry.isoformat() if creds.expiry else None
        }
        
        secret_data['gmail_token'] = json.dumps(token_data)
        
        # Update in AWS
        sm.create_or_update_secret(
            secret_name=secret_name,
            secret_value=secret_data,
            description=f"Gmail OAuth credentials for {email} (auto-updated)"
        )
        
        logger.info(f"Updated refreshed token for {email} in AWS")
        
    except Exception as e:
        logger.error(f"Failed to update token in AWS for {email}: {e}")


def get_gmail_service(email: str) -> Any:
    """Get Gmail service object for a specific email account.
    
    Args:
        email: Email address
        
    Returns:
        Gmail service object
    """
    creds = get_credentials_for_account(email)
    return build("gmail", "v1", credentials=creds)


def get_available_accounts() -> list[str]:
    """Get list of available Gmail accounts from configuration.
    
    Returns:
        List of email addresses
    """
    # For now, return the known accounts
    # This could be enhanced to read from config or environment
    accounts = []
    
    # Check which accounts have credentials in AWS
    possible_accounts = [
        "patrick@highline.work",
        "patrick.smith@gmail.com"
    ]
    
    for email in possible_accounts:
        try:
            secret_name = get_account_secret_name(email)
            # Try to get the secret to see if it exists
            get_secret(secret_name)
            accounts.append(email)
        except Exception:
            # Account not configured
            pass
    
    return accounts


def get_primary_account() -> str:
    """Get the primary email account from configuration.
    
    Returns:
        Primary email address
    """
    # Check environment variable first
    primary = os.getenv("GMAIL_PRIMARY_ACCOUNT")
    if primary:
        return primary
    
    # Check if specified in a config file
    config_path = Path(__file__).parent / "main" / "config.yaml"
    if config_path.exists():
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
            if config and "email" in config:
                return config["email"]
    
    # Default to first available account
    accounts = get_available_accounts()
    if accounts:
        return accounts[0]
    
    raise ValueError("No Gmail accounts configured")


# Backward compatibility functions
def get_credentials(
    gmail_token: str | None = None, 
    gmail_secret: str | None = None
) -> Credentials:
    """Backward compatible function to get credentials.
    
    This maintains compatibility with existing code while using
    the new multi-account system.
    """
    # Get primary account
    primary_email = get_primary_account()
    return get_credentials_for_account(primary_email)


# Re-export existing functions from original gmail module
from eaia.gmail import (
    extract_message_part,
    parse_time,
    create_message,
    get_recipients,
    send_message,
    send_email,
    search_emails
)

__all__ = [
    "get_credentials",
    "get_credentials_for_account",
    "get_gmail_service",
    "get_available_accounts",
    "get_primary_account",
    "get_account_secret_name",
    "extract_message_part",
    "parse_time",
    "create_message",
    "get_recipients",
    "send_message",
    "send_email",
    "search_emails",
]