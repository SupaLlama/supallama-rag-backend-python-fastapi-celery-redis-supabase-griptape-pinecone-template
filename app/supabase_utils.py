from enum import Enum
import logging
from typing import Dict, List, Union

from postgrest.exceptions import APIError

from gotrue.errors import AuthApiError, AuthRetryableError

from supabase import create_client, Client

from app.config import settings


# Logging Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("supabase-utils") 


# Statuses for crawled_urls Supabase table
URL_STATUS: Dict[str, str] = {
    "queued": "Queued",
    "in_progress": "In Progress",
    "completed": "Completed",
    "errored": "Errored",
}


def get_user_from_supabase_auth(encoded_access_token: str) -> Union[str, None]:
    """
    Passes the JWT to the Supabase server to retrieve the user from the database.
    """

    logger.info("In the get_user_from_supabase_auth utility function")

    if encoded_access_token is None or type(encoded_access_token) is not str:
        logger.error(f"Invalid JWT: {encoded_access_token}")
        return None

    try:
        logger.info("Create a Supabase client using the service role key")
        supabase_client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )

        logger.info("Checking Supabase auth database to verify that the user is logged in")
        supabase_user_response = supabase_client.auth.get_user(encoded_access_token)
        
        logger.info(f"Received the following UserResponse: {supabase_user_response}")
        
        # Return the user's ID
        return supabase_user_response.user.id

    except AuthRetryableError as error:
        logger.error("Supabase URL is incorrect or invalid.")
        return None
    except AuthApiError as error:
        logger.error("User is not logged in, or Supabase Service Role Key is incorrect.")
        return None
    except Exception as error:
        logger.error(error)
        return None


def insert_new_record_in_crawled_urls_table(user_id: str, url: str) -> Union[List, None]:
    """
    Inserts a new record with the URL and user_id into the crawled_urls table
    """

    logger.info("In the insert_new_record_in_crawled_urls_table utility function")

    if user_id is None or type(user_id) is not str:
        logger.error(f"Invalid user_id: {user_id}")
        return None
     
    if url is None or type(url) is not str:
        logger.error(f"Invalid URL: {url}")
        return None

    # Set initial status of new records to "Queued"
    url_status = URL_STATUS["queued"]

    try:
        logger.info("Create a Supabase client using the service role key")
        supabase_client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_ROLE_KEY
        )

        logger.info(f"Insert new record into the crawled_urls table for URL: {url} and user_id: {user_id}")
        response = (
            supabase_client.table("crawled_urls")
            .insert({
                "user_id": user_id, 
                "url": url,
                "status": url_status,
            })
            .execute()
        ) 
        
        logger.info(f"New crawled_urls record: {response}")

        # Return the newly-inserted record's data
        return response.data
    except AuthRetryableError as error:
        logger.error("Supabase URL is incorrect or invalid.")
        return None
    except APIError as error:
        logger.error("Supabase Service Role Key is incorrect.")
        return None
    except Exception as error:
        logger.error(error)
        return None


def update_status_of_record_in_crawled_urls_table(crawled_urls_id: int, user_id: str, status: str) -> None:
    """
    Updates a record in the crawled_urls table's status 
    if, and only if, the id and user_id of the record in
    the crawled_urls table "match" (i.e., this record
    was originally created on behalf of the current user)
    """

    logger.info("In the update_status_of_record_in_crawled_urls_table utility function")

    if crawled_urls_id is None or type(crawled_urls_id) is not int or crawled_urls_id < 1: 
        logger.error(f"Invalid crawled_urls_id: {crawled_urls_id}")
        return None

    if user_id is None or type(user_id) is not str or len(user_id.trim()) == 0:
        logger.error(f"Invalid user_id: {user_id}")
        return None
     
    if status is None or type(status) is not str or len(status.trim()) == 0:
        logger.error(f"Invalid status: {status}")
        return None

    try:
        logger.info("Create a Supabase client using the service role key")
        supabase_client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_ROLE_KEY
        )

        logger.info(f"Update status to {status} for crawled_urls row ID: {crawled_urls_id} for user_id: {user_id}")
        response = (
            supabase_client.table("crawled_urls")
            .update({
                "status": status,
            })
            .eq("id", crawled_urls_id)
            .eq("user_id", user_id)
            .execute()
        ) 
        
        logger.info(f"Update crawled_urls record response: {response}")

        # Return the updated record's data
        return response.data
    except AuthRetryableError as error:
        logger.error("Supabase URL is incorrect or invalid.")
        return None
    except APIError as error:
        logger.error("Supabase Service Role Key is incorrect.")
        return None
    except Exception as error:
        logger.error(error)
        return None

     