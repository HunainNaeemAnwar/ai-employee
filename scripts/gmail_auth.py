"""
Gmail OAuth2 Authentication Script

Run this script once to authenticate with Gmail API.
It will open a browser window for you to grant permissions.
The token is saved to SECURITY/gmail_token.json.
"""

import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.secrets import get_secrets


def authenticate_gmail(vault_path: str) -> str:
    """
    Run Gmail OAuth2 authentication flow.
    
    Args:
        vault_path: Path to AI_Employee_Vault
        
    Returns:
        Path to saved token file
        
    Raises:
        ImportError: If required Google libraries are not installed
        ValueError: If credentials are not configured
    """
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError as e:
        raise ImportError(
            "Google API libraries not installed. Run:\n"
            "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        ) from e
    
    # Load secrets
    secrets = get_secrets(vault_path)
    
    # Check if credentials exist
    credentials_file = os.path.join(vault_path, "SECURITY/credentials.json")
    token_file = os.path.join(vault_path, "SECURITY/gmail_token.json")
    
    if not os.path.exists(credentials_file):
        raise ValueError(
            f"credentials.json not found at {credentials_file}\n"
            "Please download it from Google Cloud Console:\n"
            "1. Go to https://console.cloud.google.com/\n"
            "2. Create/select project\n"
            "3. Enable Gmail API\n"
            "4. Create OAuth2 credentials (Desktop app)\n"
            "5. Download credentials.json to SECURITY/"
        )
    
    # OAuth2 scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.labels',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    creds = None
    
    # Load existing token
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Run OAuth2 flow
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES
            )
            creds = flow.run_local_server(port=8080)
        
        # Save token
        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
        
        print(f"✅ Token saved to {token_file}")
    else:
        print(f"✅ Using existing token at {token_file}")
    
    # Test connection
    try:
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Connected to Gmail: {profile['emailAddress']}")
    except Exception as e:
        print(f"⚠️ Connection test failed: {e}")
    
    return token_file


def check_auth(vault_path: str) -> bool:
    """
    Check if Gmail authentication exists and is valid.
    
    Args:
        vault_path: Path to AI_Employee_Vault
        
    Returns:
        True if authenticated, False otherwise
    """
    token_file = os.path.join(vault_path, "SECURITY/gmail_token.json")
    
    if not os.path.exists(token_file):
        return False
    
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        
        secrets = get_secrets(vault_path)
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.labels',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        # Refresh if needed
        if not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token
            with open(token_file, 'w') as f:
                f.write(creds.to_json())
        
        return creds.valid
    
    except Exception:
        return False


def main():
    """Main entry point."""
    # Default vault path
    vault_path = os.environ.get(
        "VAULT_PATH",
        "/home/hunain/personal_assistant/AI_Employee_Vault"
    )
    
    print("🔐 Gmail OAuth2 Authentication")
    print("=" * 40)
    
    # Check if already authenticated
    if check_auth(vault_path):
        print("✅ Already authenticated!")
        return
    
    print("\n📋 Instructions:")
    print("1. A browser window will open")
    print("2. Sign in with your Google account")
    print("3. Grant Gmail API permissions")
    print("4. Browser will redirect to localhost")
    print("5. Token will be saved automatically\n")
    
    input("Press Enter to start authentication...")
    
    try:
        token_path = authenticate_gmail(vault_path)
        print(f"\n✅ Authentication complete!")
        print(f"Token saved to: {token_path}")
    except ImportError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
