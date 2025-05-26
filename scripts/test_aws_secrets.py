#!/usr/bin/env python3
"""Test AWS Secrets Manager integration."""

import boto3
import json
import os
from datetime import datetime
from botocore.exceptions import ClientError


def get_secret(secret_name, region_name="us-west-2"):
    """Retrieve a secret from AWS Secrets Manager."""
    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    
    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)


def list_secrets(region_name="us-west-2"):
    """List all secrets in AWS Secrets Manager."""
    
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        response = client.list_secrets()
        return response.get('SecretList', [])
    except ClientError as e:
        print(f"Error listing secrets: {e}")
        return []


def create_secret(secret_name, secret_value, region_name="us-west-2"):
    """Create a new secret in AWS Secrets Manager."""
    
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        response = client.create_secret(
            Name=secret_name,
            SecretString=json.dumps(secret_value)
        )
        return response
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceExistsException':
            print(f"Secret {secret_name} already exists. Updating instead...")
            response = client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(secret_value)
            )
            return response
        else:
            raise e


if __name__ == "__main__":
    # Test AWS configuration
    print("Testing AWS Secrets Manager...")
    print("-" * 50)
    
    # Check AWS credentials
    session = boto3.Session()
    credentials = session.get_credentials()
    if credentials:
        print("✅ AWS credentials found")
        print(f"   Access Key: ...{credentials.access_key[-4:]}")
        region = session.region_name or os.environ.get('AWS_REGION', 'Not set')
        print(f"   Region: {region}")
    else:
        print("❌ No AWS credentials found")
        print("   Please configure AWS CLI: aws configure")
        exit(1)
    
    print("\n" + "-" * 50)
    
    # List existing secrets
    print("\nListing secrets...")
    secrets = list_secrets()
    if secrets:
        print(f"Found {len(secrets)} secret(s):")
        for secret in secrets:
            print(f"  - {secret['Name']}")
    else:
        print("No secrets found or unable to list secrets")
    
    # Example: Create/update a test secret
    test_secret_name = "eaia/test-secret"
    test_secret_value = {
        "test_key": "test_value",
        "timestamp": str(datetime.now())
    }
    
    print(f"\nCreating/updating test secret: {test_secret_name}")
    try:
        result = create_secret(test_secret_name, test_secret_value)
        print("✅ Secret created/updated successfully")
        print(f"   ARN: {result.get('ARN', 'N/A')}")
    except Exception as e:
        print(f"❌ Error creating secret: {e}")
    
    # Example: Retrieve the test secret
    print(f"\nRetrieving test secret: {test_secret_name}")
    try:
        secret_data = get_secret(test_secret_name)
        print("✅ Secret retrieved successfully:")
        print(f"   Data: {json.dumps(secret_data, indent=2)}")
    except Exception as e:
        print(f"❌ Error retrieving secret: {e}") 