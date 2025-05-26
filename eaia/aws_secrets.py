"""AWS Secrets Manager integration for EAIA."""

import json
import logging
import os
from typing import Dict, Any, Optional
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SecretsManager:
    """AWS Secrets Manager client wrapper."""
    
    def __init__(self, region_name: Optional[str] = None):
        """Initialize the Secrets Manager client.
        
        Args:
            region_name: AWS region name. Defaults to environment variable
                        AWS_REGION or us-east-1.
        """
        self.region_name = (
            region_name or os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.client = boto3.client(
            service_name='secretsmanager',
            region_name=self.region_name
        )
    
    @lru_cache(maxsize=128)
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve a secret from AWS Secrets Manager.
        
        Args:
            secret_name: Name or ARN of the secret to retrieve.
            
        Returns:
            Dictionary containing the secret data.
            
        Raises:
            ClientError: If the secret cannot be retrieved.
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            
            # Secrets Manager returns either SecretString or SecretBinary
            if 'SecretString' in response:
                secret = response['SecretString']
                # Try to parse as JSON, otherwise return as string
                try:
                    return json.loads(secret)
                except json.JSONDecodeError:
                    return {'value': secret}
            else:
                # Binary secrets not supported in this implementation
                raise ValueError(f"Binary secret {secret_name} not supported")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.error(f"Secret {secret_name} not found")
            elif error_code == 'InvalidRequestException':
                logger.error(f"Invalid request for secret {secret_name}")
            elif error_code == 'InvalidParameterException':
                logger.error(f"Invalid parameter for secret {secret_name}")
            elif error_code == 'DecryptionFailure':
                logger.error(f"Cannot decrypt secret {secret_name}")
            elif error_code == 'InternalServiceError':
                logger.error(
                    f"Internal service error retrieving {secret_name}"
                )
            else:
                logger.error(
                    f"Unknown error retrieving {secret_name}: {error_code}"
                )
            raise
    
    def create_or_update_secret(
        self, 
        secret_name: str, 
        secret_value: Dict[str, Any],
        description: Optional[str] = None
    ) -> str:
        """Create or update a secret in AWS Secrets Manager.
        
        Args:
            secret_name: Name of the secret to create/update.
            secret_value: Dictionary containing the secret data.
            description: Optional description for the secret.
            
        Returns:
            ARN of the created/updated secret.
        """
        secret_string = json.dumps(secret_value)
        
        try:
            # Try to create the secret
            response = self.client.create_secret(
                Name=secret_name,
                Description=description or f"Secret for {secret_name}",
                SecretString=secret_string
            )
            logger.info(f"Created secret {secret_name}")
            return response['ARN']
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                # Secret exists, update it instead
                response = self.client.update_secret(
                    SecretId=secret_name,
                    SecretString=secret_string
                )
                logger.info(f"Updated existing secret {secret_name}")
                return response['ARN']
            else:
                raise
    
    def delete_secret(self, secret_name: str, force: bool = False) -> None:
        """Delete a secret from AWS Secrets Manager.
        
        Args:
            secret_name: Name or ARN of the secret to delete.
            force: If True, immediately delete without recovery window.
        """
        try:
            if force:
                self.client.delete_secret(
                    SecretId=secret_name,
                    ForceDeleteWithoutRecovery=True
                )
                logger.info(f"Force deleted secret {secret_name}")
            else:
                self.client.delete_secret(
                    SecretId=secret_name,
                    RecoveryWindowInDays=7
                )
                logger.info(f"Scheduled deletion of secret {secret_name} in 7 days")
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning(f"Secret {secret_name} not found for deletion")
            else:
                raise


# Global instance for convenience
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get or create the global SecretsManager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_secret(secret_name: str) -> Dict[str, Any]:
    """Convenience function to get a secret using the global instance."""
    return get_secrets_manager().get_secret(secret_name)


def get_gmail_credentials_from_aws() -> tuple[str, str]:
    """Retrieve Gmail credentials from AWS Secrets Manager.
    
    Returns:
        Tuple of (gmail_secret, gmail_token)
    """
    try:
        # Get Gmail credentials from AWS Secrets Manager
        gmail_creds = get_secret("eaia/gmail-credentials")
        
        gmail_secret = gmail_creds.get("gmail_secret", "")
        gmail_token = gmail_creds.get("gmail_token", "")
        
        if not gmail_secret or not gmail_token:
            raise ValueError("Gmail credentials incomplete in AWS Secrets Manager")
            
        return gmail_secret, gmail_token
        
    except Exception as e:
        logger.error(f"Failed to retrieve Gmail credentials from AWS: {e}")
        raise 