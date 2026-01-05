from typing import Optional
from google.auth.transport import requests
from google.oauth2 import id_token
from app.config.env import settings
from app.common.exceptions import GoogleOAuthException
import logging

logger = logging.getLogger(__name__)


async def verify_google_token(id_token_string: str) -> Optional[dict]:
    """Verifikasi Google ID token dan return user info."""
    try:
        request = requests.Request()
        user_info = id_token.verify_oauth2_token(
            id_token_string,
            request,
            settings.GOOGLE_CLIENT_ID
        )
        if user_info.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer')
        return user_info
    except ValueError as e:
        logger.error(f"Google token verification failed: {e}")
        raise GoogleOAuthException(f"Invalid Google token: {str(e)}")
    except Exception as e:
        logger.error(f"Error verifying Google token: {e}")
        raise GoogleOAuthException("Failed to verify Google token")


def extract_google_user_data(user_info: dict) -> tuple[str, str, str]:
    """Ekstrak user data dari Google token response."""
    google_id = user_info.get('sub')
    email = user_info.get('email')
    name = user_info.get('name', email.split('@')[0])
    if not google_id or not email:
        raise GoogleOAuthException("Missing required user information from Google")
    username = name.lower().replace(' ', '_')
    return google_id, email, username

