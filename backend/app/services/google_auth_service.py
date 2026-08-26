from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings


class GoogleAuthService:

    def verify_google_token(
        self,
        token: str
    ) -> dict:
        """
        Verify a Google ID token and return
        the authenticated user's information.
        """

        try:

            google_request = requests.Request()

            user_info = id_token.verify_oauth2_token(
                token,
                google_request,
                settings.GOOGLE_CLIENT_ID
            )

            return {
                "google_id": user_info["sub"],
                "email": user_info["email"],
                "name": user_info.get("name"),
                "profile_picture_url": user_info.get("picture")
            }

        except ValueError:

            raise ValueError(
                "Invalid Google authentication token"
            )