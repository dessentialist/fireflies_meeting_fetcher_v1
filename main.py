#!/usr/bin/env python3
"""
Fireflies Meeting Fetcher - Main Script

This script orchestrates the entire process of fetching meeting transcripts
from the Fireflies.ai API and saving them as markdown files.

Usage:
    python main.py

The script will:
1. Load configuration from .env file
2. Connect to Fireflies API
3. Fetch transcripts from the last 2 months (configurable)
4. Download detailed transcript content for each meeting
5. Format and save transcripts as markdown files
6. Provide a summary of the operation
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import Config, ensure_output_directory, setup_logging
from fireflies_client import FirefliesAPIError, FirefliesClient
from transcript_formatter import TranscriptFormatter


class FirefliesFetcher:
    """
    Main orchestrator class for the Fireflies Meeting Fetcher.

    This class coordinates all operations including configuration loading,
    API communication, data processing, and file output.
    """

    def __init__(self):
        """Initialize the fetcher with configuration and logging."""
        self.logger = setup_logging("INFO")
        self.config = None
        self.client = None
        self.formatter = None
        self.stats = {
            "total_transcripts": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "skipped_files": 0,
            "start_time": None,
            "end_time": None,
        }

    def initialize(self) -> bool:
        """
        Initialize all components and validate configuration.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("🚀 Initializing Fireflies Meeting Fetcher...")

            # Load configuration
            self.logger.info("📋 Loading configuration...")
            self.config = Config()

            # Ensure output directory exists
            ensure_output_directory(self.config.output_directory)

            # Initialize API client
            self.logger.info("🔑 Initializing API client...")
            self.client = FirefliesClient(
                api_key=self.config.api_key,
                base_url=self.config.api_base_url,
                logger=self.logger,
            )

            # Test API connection
            self.logger.info("🔌 Testing API connection...")
            if not self.client.validate_api_key():
                self.logger.error(
                    "❌ API key validation failed. Please check your FIREFLIES_API_KEY."
                )
                return False

            # Initialize formatter
            self.logger.info("📝 Initializing transcript formatter...")
            self.formatter = TranscriptFormatter(
                output_directory=self.config.output_directory, logger=self.logger
            )

            self.logger.info("✅ Initialization complete!")
            return True

        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {str(e)}")
            return False

    def fetch_transcript_list(self) -> List[Dict[str, Any]]:
        """
        Fetch the list of transcripts in the configured date range.

        Returns:
            List of transcript metadata dictionaries
        """
        try:
            self.logger.info("📅 Calculating date range...")
            from_date, to_date = self.config.get_date_range_iso()

            self.logger.info(f"📊 Fetching transcripts from {from_date} to {to_date}")

            # Fetch all transcripts in the date range
            transcripts = self.client.fetch_all_transcripts_in_range(
                from_date=from_date,
                to_date=to_date,
                max_per_query=self.config.max_transcripts_per_query,
            )

            self.stats["total_transcripts"] = len(transcripts)
            self.logger.info(f"📋 Found {len(transcripts)} transcripts to process")

            return transcripts

        except FirefliesAPIError as e:
            self.logger.error(f"❌ API error while fetching transcript list: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(
                f"❌ Unexpected error while fetching transcript list: {str(e)}"
            )
            raise

    def process_transcript(self, transcript_metadata: Dict[str, Any]) -> bool:
        """
        Process a single transcript: fetch details and save as markdown.

        Args:
            transcript_metadata: Basic transcript metadata from the list

        Returns:
            True if processing successful, False otherwise
        """
        transcript_id = transcript_metadata.get("id")
        title = transcript_metadata.get("title", "Unknown Meeting")

        try:
            self.logger.info(f"📥 Processing: {title}")

            # Fetch detailed transcript content
            detailed_transcript = self.client.fetch_transcript_details(transcript_id)

            # Save as markdown file
            file_path = self.formatter.save_transcript(detailed_transcript)

            self.stats["successful_downloads"] += 1
            self.logger.info(f"✅ Saved: {file_path.name}")

            return True

        except FirefliesAPIError as e:
            self.logger.error(f"❌ API error processing '{title}': {str(e)}")
            self.stats["failed_downloads"] += 1
            return False
        except Exception as e:
            self.logger.error(f"❌ Error processing '{title}': {str(e)}")
            self.stats["failed_downloads"] += 1
            return False

    def process_all_transcripts(self, transcripts: List[Dict[str, Any]]) -> None:
        """
        Process all transcripts with progress tracking.

        Args:
            transcripts: List of transcript metadata to process
        """
        if not transcripts:
            self.logger.info("📭 No transcripts to process")
            return

        self.logger.info(f"🔄 Starting to process {len(transcripts)} transcripts...")

        for i, transcript in enumerate(transcripts, 1):
            # Progress indicator
            progress = f"[{i}/{len(transcripts)}]"
            self.logger.info(
                f"📊 {progress} Processing transcript {i} of {len(transcripts)}"
            )

            # Process the transcript
            self.process_transcript(transcript)

            # Small delay to be respectful to the API
            if i < len(transcripts):  # Don't delay after the last one
                time.sleep(0.5)

        self.logger.info("🏁 Finished processing all transcripts")

    def generate_summary_report(self) -> None:
        """Generate and display a summary report of the operation."""
        duration = (
            self.stats["end_time"] - self.stats["start_time"]
            if self.stats["start_time"]
            else None
        )

        self.logger.info("📊 " + "=" * 60)
        self.logger.info("📊 FIReflies Meeting Fetcher - Summary Report")
        self.logger.info("📊 " + "=" * 60)
        self.logger.info(
            f"📊 Total transcripts found: {self.stats['total_transcripts']}"
        )
        self.logger.info(
            f"📊 Successfully downloaded: {self.stats['successful_downloads']}"
        )
        self.logger.info(f"📊 Failed downloads: {self.stats['failed_downloads']}")
        success_rate = (
            self.stats["successful_downloads"] / max(1, self.stats["total_transcripts"])
        ) * 100
        self.logger.info(f"📊 Success rate: {success_rate:.1f}%")

        if duration:
            self.logger.info(f"📊 Total time: {duration:.1f} seconds")

        # File statistics
        file_stats = self.formatter.get_file_stats()
        self.logger.info(f"📊 Files in output directory: {file_stats['total_files']}")
        self.logger.info(f"📊 Total size: {file_stats['total_size_mb']} MB")

        self.logger.info("📊 " + "=" * 60)

        if self.stats["failed_downloads"] > 0:
            failed_count = self.stats["failed_downloads"]
            self.logger.warning(
                f"⚠️  {failed_count} transcripts failed to download. "
                "Check the logs above for details."
            )

    def run(self) -> bool:
        """
        Run the complete fetching process.

        Returns:
            True if the process completed successfully, False otherwise
        """
        try:
            # Record start time
            self.stats["start_time"] = time.time()

            # Initialize components
            if not self.initialize():
                return False

            # Fetch transcript list
            transcripts = self.fetch_transcript_list()

            # Process all transcripts
            self.process_all_transcripts(transcripts)

            # Record end time
            self.stats["end_time"] = time.time()

            # Generate summary report
            self.generate_summary_report()

            # Return success if we processed at least some transcripts successfully
            return self.stats["successful_downloads"] > 0

        except KeyboardInterrupt:
            self.logger.info("⏹️  Operation cancelled by user")
            return False
        except Exception as e:
            self.logger.error(f"❌ Fatal error: {str(e)}")
            return False


def print_usage():
    """Print usage information."""
    print(
        """
🔥 Fireflies Meeting Fetcher v1

This script fetches meeting transcripts from Fireflies.ai and saves them as markdown files.

Setup:
1. Copy .env.example to .env
2. Add your Fireflies API key to .env
3. Run: python main.py

Configuration:
- FIREFLIES_API_KEY: Your API key (required)
- OUTPUT_DIRECTORY: Where to save files (default: 'transcripts')
- MONTHS_TO_FETCH: How many months back to fetch (default: 2)
- MAX_TRANSCRIPTS_PER_QUERY: API query limit (default: 50)

For more information, see index.md
"""
    )


def main():
    """Main entry point for the script."""
    try:
        # Check if help is requested
        if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
            print_usage()
            return 0

        # Create and run the fetcher
        fetcher = FirefliesFetcher()
        success = fetcher.run()

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
