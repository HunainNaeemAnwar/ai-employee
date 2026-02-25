#!/usr/bin/env python3
"""
Gmail OAuth2 Authentication Script

Run this script to authenticate with Gmail API and create the token file.
The token will be saved to AI_Employee_Vault/.system/gmail_token.json

Usage:
    python scripts/gmail_auth.py

Requirements:
    - Gmail API enabled in Google Cloud Console
    - OAuth 2.0 credentials (client_id, client_secret)
    - credentials.json file in AI_Employee_Vault/.system/
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings


def authenticate_gmail():
    """Authenticate with Gmail API using OAuth2."""
    print("🔐 Gmail OAuth2 Authentication")
    print("=" * 60)
    
    settings = Settings()
    vault_path = Path(settings.vault_path)
    
    # Token and credentials locations
    token_file = vault_path / ".system" / "gmail_token.json"
    credentials_file = vault_path / ".system" / "credentials.json"
    
    # Also check old SECURITY/ location for migration
    if not credentials_file.exists():
        old_credentials = vault_path / "SECURITY" / "credentials.json"
        if old_credentials.exists():
            print(f"📂 Found credentials in old location, copying...")
            import shutil
            token_file = vault_path / ".system" / "gmail_token.json"
            token_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(old_credentials, credentials_file)
    
    # Check if credentials file exists
    if not credentials_file.exists():
        print(f"❌ Error: credentials.json not found at {credentials_file}")
        print()
        print("To get credentials:")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("2. Enable Gmail API")
        print("3. Create OAuth 2.0 credentials")
        print("4. Download credentials.json")
        print(f"5. Save it to: {credentials_file}")
        return False
    
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        
        # Define scopes
        scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.labels',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        
        creds = None
        
        # Load existing token
        if token_file.exists():
            print(f"📂 Found existing token: {token_file}")
            creds = Credentials.from_authorized_user_file(str(token_file), scopes)
        
        # Refresh or re-authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Refreshing expired token...")
                try:
                    creds.refresh(Request())
                    print("✅ Token refreshed successfully")
                except Exception as e:
                    print(f"⚠️ Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                print("🌐 Opening browser for OAuth authentication...")
                print("   Please complete the authentication in your browser.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_file), scopes
                )
                
                # Run local server for OAuth callback
                creds = flow.run_local_server(
                    port=8080,
                    bind_addr="127.0.0.1",
                    open_browser=True
                )
                
                print("✅ Authentication successful!")
        
        # Save token
        token_file.parent.mkdir(parents=True, exist_ok=True)
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
        
        print(f"💾 Token saved to: {token_file}")
        print()
        print("✅ Gmail authentication complete!")
        print()
        print("Next steps:")
        print("1. Run: python main.py start")
        print("2. Gmail Watcher will now poll for new emails")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: credentials.json not found")
        print(f"   Expected at: {credentials_file}")
        return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure credentials.json is valid")
        print("2. Make sure Gmail API is enabled")
        print("3. Try deleting the token file and re-authenticating")
        return False


def test_authentication():
    """Test Gmail authentication by making a simple API call."""
    print("🧪 Testing Gmail authentication...")
    print("=" * 60)
    
    settings = Settings()
    vault_path = Path(settings.vault_path)
    token_file = vault_path / ".system" / "gmail_token.json"
    
    if not token_file.exists():
        print("❌ Token file not found. Run authentication first:")
        print("   python scripts/gmail_auth.py")
        return False
    
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
        ]
        
        creds = Credentials.from_authorized_user_file(str(token_file), scopes)
        
        if not creds.valid:
            print("❌ Token is invalid or expired")
            print("   Re-run: python scripts/gmail_auth.py")
            return False
        
        # Build service and test
        service = build('gmail', 'v1', credentials=creds)
        
        # Try to list labels (simple test)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        print(f"✅ Authentication successful!")
        print(f"   Found {len(labels)} Gmail labels")
        print(f"   Token valid until: {creds.expiry}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gmail OAuth2 Authentication"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test existing authentication"
    )
    
    args = parser.parse_args()
    
    if args.test:
        success = test_authentication()
    else:
        success = authenticate_gmail()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
