"""
Fireflies API Client for Meeting Transcript Fetcher

This module provides a robust client for interacting with the Fireflies.ai GraphQL API.
It handles authentication, query construction, error handling, and response parsing.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class FirefliesAPIError(Exception):
    """Custom exception for Fireflies API specific errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        response_data: Optional[Dict] = None,
    ):
        """
        Initialize Fireflies API error.

        Args:
            message: Error message
            error_code: API error code if available
            response_data: Full response data for debugging
        """
        super().__init__(message)
        self.error_code = error_code
        self.response_data = response_data


class FirefliesClient:
    """
    Client for interacting with the Fireflies.ai GraphQL API.

    This class provides methods to authenticate, query transcripts, and handle
    API responses with proper error handling and retry logic.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.fireflies.ai/graphql",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the Fireflies API client.

        Args:
            api_key: Fireflies API key for authentication
            base_url: Base URL for the Fireflies GraphQL API
            logger: Logger instance for logging operations
        """
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logger or logging.getLogger(__name__)

        # Create session with retry strategy
        self.session = self._create_session()

        # Validate API key format (basic validation only)
        if not self.api_key or len(self.api_key.strip()) < 10:
            raise FirefliesAPIError("API key appears to be invalid or too short")

        self.logger.info("FirefliesClient initialized successfully")

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy and proper headers.

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Set default headers
        session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "Fireflies-Meeting-Fetcher/1.0",
            }
        )

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # Total number of retries
            status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry
            allowed_methods=["POST"],  # Only retry POST requests
            backoff_factor=1,  # Exponential backoff factor
            raise_on_status=False,  # Don't raise exceptions on retry
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def validate_api_key(self) -> bool:
        """
        Validate API key by making a test request.

        Returns:
            True if API key is valid, False otherwise
        """
        # Make a simple test request to validate the API key
        test_query = """
        query {
            user {
                user_id
                email
            }
        }
        """

        try:
            self._make_graphql_request(test_query, {})
            self.logger.info("API key validation successful")
            return True
        except FirefliesAPIError as e:
            if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                self.logger.error(
                    "Invalid API key. Please check your FIREFLIES_API_KEY in .env file"
                )
                return False
            else:
                # Re-raise other API errors
                raise
        except Exception as e:
            self.logger.error(f"Failed to validate API key: {str(e)}")
            return False

    def _make_graphql_request(
        self, query: str, variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make a GraphQL request to the Fireflies API.

        Args:
            query: GraphQL query string
            variables: Variables for the query

        Returns:
            Parsed JSON response data

        Raises:
            FirefliesAPIError: If the request fails or returns errors
        """
        payload = {"query": query, "variables": variables}

        try:
            self.logger.debug(f"Making GraphQL request: {query[:100]}...")
            self.logger.debug(f"Variables: {variables}")

            response = self.session.post(
                self.base_url, json=payload, timeout=30  # 30 second timeout
            )

            # Log response status
            self.logger.debug(f"Response status: {response.status_code}")

            # Handle HTTP errors
            if response.status_code == 401:
                raise FirefliesAPIError(
                    "Authentication failed. Please check your API key."
                )
            elif response.status_code == 429:
                raise FirefliesAPIError("Rate limit exceeded. Please try again later.")
            elif response.status_code >= 400:
                raise FirefliesAPIError(
                    f"HTTP error {response.status_code}: {response.text}"
                )

            # Parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                raise FirefliesAPIError(f"Invalid JSON response: {str(e)}")

            # Check for GraphQL errors
            if "errors" in data and data["errors"]:
                error_messages = [
                    error.get("message", "Unknown error") for error in data["errors"]
                ]
                error_codes = [
                    error.get("extensions", {}).get("code") for error in data["errors"]
                ]
                raise FirefliesAPIError(
                    f"GraphQL errors: {'; '.join(error_messages)}",
                    error_code=error_codes[0] if error_codes else None,
                    response_data=data,
                )

            # Check for missing data
            if "data" not in data:
                raise FirefliesAPIError("No data in response", response_data=data)

            return data["data"]

        except requests.exceptions.Timeout:
            raise FirefliesAPIError(
                "Request timed out. Please check your internet connection."
            )
        except requests.exceptions.ConnectionError:
            raise FirefliesAPIError(
                "Connection error. Please check your internet connection."
            )
        except requests.exceptions.RequestException as e:
            raise FirefliesAPIError(f"Request failed: {str(e)}")

    def fetch_transcripts(
        self, from_date: str, to_date: str, limit: int = 50, skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch transcripts within a date range.

        Args:
            from_date: Start date in ISO 8601 format (e.g., "2024-01-01T00:00:00.000Z")
            to_date: End date in ISO 8601 format (e.g., "2024-03-01T00:00:00.000Z")
            limit: Maximum number of transcripts to return (max 50)
            skip: Number of transcripts to skip for pagination

        Returns:
            List of transcript metadata dictionaries

        Raises:
            FirefliesAPIError: If the request fails
        """
        # Validate inputs
        if limit > 50:
            raise ValueError("Limit cannot exceed 50 (API maximum)")

        if skip < 0:
            raise ValueError("Skip cannot be negative")

        # Construct GraphQL query for transcripts list
        query = """
        query Transcripts($fromDate: DateTime, $toDate: DateTime, $limit: Int, $skip: Int) {
            transcripts(
                fromDate: $fromDate, toDate: $toDate, limit: $limit, skip: $skip
            ) {
                id
                title
                organizer_email
                participants
                fireflies_users
                duration
                dateString
                date
                transcript_url
            }
        }
        """

        variables = {
            "fromDate": from_date,
            "toDate": to_date,
            "limit": limit,
            "skip": skip,
        }

        try:
            self.logger.info(f"Fetching transcripts from {from_date} to {to_date}")
            data = self._make_graphql_request(query, variables)

            transcripts = data.get("transcripts", [])
            self.logger.info(f"Retrieved {len(transcripts)} transcripts")

            return transcripts

        except FirefliesAPIError:
            raise
        except Exception as e:
            raise FirefliesAPIError(f"Failed to fetch transcripts: {str(e)}")

    def fetch_transcript_details(self, transcript_id: str) -> Dict[str, Any]:
        """
        Fetch detailed transcript content including sentences and speakers.

        Args:
            transcript_id: Unique identifier of the transcript

        Returns:
            Detailed transcript data including sentences and speakers

        Raises:
            FirefliesAPIError: If the request fails
        """
        if not transcript_id or not transcript_id.strip():
            raise ValueError("Transcript ID cannot be empty")

        # Construct GraphQL query for detailed transcript
        query = """
        query Transcript($transcriptId: String!) {
            transcript(id: $transcriptId) {
                id
                title
                organizer_email
                participants
                fireflies_users
                duration
                dateString
                date
                transcript_url
                speakers {
                    id
                    name
                }
                sentences {
                    text
                    speaker_name
                    start_time
                    end_time
                }
                summary {
                    action_items
                    keywords
                    outline
                }
            }
        }
        """

        variables = {"transcriptId": transcript_id}

        try:
            self.logger.info(f"Fetching detailed transcript: {transcript_id}")
            data = self._make_graphql_request(query, variables)

            transcript = data.get("transcript")
            if not transcript:
                raise FirefliesAPIError(f"Transcript not found: {transcript_id}")

            self.logger.info(
                f"Retrieved detailed transcript: {transcript.get('title', 'Unknown')}"
            )
            return transcript

        except FirefliesAPIError:
            raise
        except Exception as e:
            raise FirefliesAPIError(f"Failed to fetch transcript details: {str(e)}")

    def fetch_all_transcripts_in_range(
        self, from_date: str, to_date: str, max_per_query: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch all transcripts in a date range, handling pagination automatically.

        Args:
            from_date: Start date in ISO 8601 format
            to_date: End date in ISO 8601 format
            max_per_query: Maximum transcripts per query (default 50)

        Returns:
            Complete list of all transcripts in the date range

        Raises:
            FirefliesAPIError: If any request fails
        """
        all_transcripts = []
        skip = 0

        self.logger.info(f"Fetching all transcripts from {from_date} to {to_date}")

        while True:
            # Fetch batch of transcripts
            transcripts = self.fetch_transcripts(
                from_date=from_date, to_date=to_date, limit=max_per_query, skip=skip
            )

            # If no transcripts returned, we've reached the end
            if not transcripts:
                break

            all_transcripts.extend(transcripts)
            self.logger.info(
                f"Retrieved {len(transcripts)} transcripts (total: {len(all_transcripts)})"
            )

            # If we got fewer than the limit, we've reached the end
            if len(transcripts) < max_per_query:
                break

            # Prepare for next batch
            skip += max_per_query

            # Small delay to be respectful to the API
            time.sleep(0.1)

        self.logger.info(
            f"Finished fetching transcripts. Total: {len(all_transcripts)}"
        )
        return all_transcripts

    def test_connection(self) -> bool:
        """
        Test the connection to the Fireflies API.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple query to test connection
            query = """
            query {
                user {
                    user_id
                }
            }
            """
            self._make_graphql_request(query, {})
            self.logger.info("Connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
