import jwt
import logging

from app.config import settings


# Logging Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jwt-utils") 


def verify_jwt(encoded_token: str, audience: str) -> bool:
    """Decode and verify JWT using HS256 and env variables"""

    logger.info("In the verify_jwt utility function")

    if encoded_token is None or type(encoded_token) is not str:
        logger.error(f"Invalid JWT: {encoded_token}")
        return False

    if audience is None or type(audience) is not str:
        logger.error(f"Invalid JWT audience: {audience}")
        return False

    try:
        logger.info("Decoding JWT with secret to verify it")
        decoded_token = jwt.decode(
            encoded_token,
            key=settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256",],
            audience=["authenticated",]
        )

        logger.info(f"Decoded JWT: {decoded_token}")
        return True
    except Exception as error:
        logger.error(error)
        return False
