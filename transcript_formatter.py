"""
Transcript Formatter for Fireflies Meeting Fetcher

This module handles the conversion of Fireflies API transcript data into
well-formatted markdown files with proper metadata and content structure.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class TranscriptFormatter:
    """
    Handles formatting and saving of transcript data as markdown files.

    This class provides methods to sanitize filenames, format transcript content,
    and save files with proper structure and metadata.
    """

    def __init__(
        self,
        output_directory: str = "transcripts",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the transcript formatter.

        Args:
            output_directory: Directory to save transcript files
            logger: Logger instance for logging operations
        """
        self.output_directory = Path(output_directory)
        self.logger = logger or logging.getLogger(__name__)

        # Ensure output directory exists
        self.output_directory.mkdir(parents=True, exist_ok=True)

        self.logger.info(
            f"TranscriptFormatter initialized with output directory: "
            f"{self.output_directory}"
        )

    def sanitize_filename(self, title: str, max_length: int = 100) -> str:
        """
        Sanitize a meeting title to create a valid filename.

        Args:
            title: Original meeting title
            max_length: Maximum length of the filename (excluding extension)

        Returns:
            Sanitized filename (without extension)
        """
        if not title or not title.strip():
            # Generate a default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"meeting_{timestamp}"

        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*!]', "_", title.strip())

        # Replace multiple spaces/underscores with single underscore
        sanitized = re.sub(r"[_\s]+", "_", sanitized)

        # Remove leading/trailing underscores and dots
        sanitized = sanitized.strip("_.")

        # Ensure it's not empty after sanitization
        if not sanitized:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"meeting_{timestamp}"

        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip("_.")

        return sanitized

    def format_duration(self, duration_minutes: Optional[float]) -> str:
        """
        Format duration from minutes to human-readable format.

        Args:
            duration_minutes: Duration in minutes (can be float)

        Returns:
            Formatted duration string
        """
        if not duration_minutes:
            return "Unknown"

        try:
            duration = float(duration_minutes)
            hours = int(duration // 60)
            minutes = int(duration % 60)

            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except (ValueError, TypeError):
            return "Unknown"

    def format_date(self, date_string: Optional[str]) -> str:
        """
        Format date string to human-readable format.

        Args:
            date_string: ISO 8601 date string from API

        Returns:
            Formatted date string
        """
        if not date_string:
            return "Unknown"

        try:
            # Parse ISO 8601 date
            dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
            return dt.strftime("%B %d, %Y at %I:%M %p UTC")
        except (ValueError, AttributeError):
            return date_string  # Return original if parsing fails

    def format_participants(
        self, participants: List[str], fireflies_users: List[str]
    ) -> str:
        """
        Format participant lists into a readable string.

        Args:
            participants: List of all participant emails
            fireflies_users: List of Fireflies user emails

        Returns:
            Formatted participants string
        """
        if not participants and not fireflies_users:
            return "No participants recorded"

        # Ensure we have lists, not other data types
        if not isinstance(participants, list):
            participants = []
        if not isinstance(fireflies_users, list):
            fireflies_users = []

        # Combine and deduplicate participants
        all_participants = list(set(participants + fireflies_users))

        if len(all_participants) <= 5:
            return ", ".join(all_participants)
        else:
            # Show first 3 and count of remaining
            shown = all_participants[:3]
            remaining = len(all_participants) - 3
            return f"{', '.join(shown)} and {remaining} others"

    def format_transcript_sentences(self, sentences: List[Dict[str, Any]]) -> str:
        """
        Format transcript sentences into readable markdown.

        Args:
            sentences: List of sentence dictionaries from API

        Returns:
            Formatted transcript content
        """
        if not sentences:
            return "No transcript content available."

        formatted_content = []

        for sentence in sentences:
            # Extract sentence data
            text = sentence.get("text", "").strip()
            speaker_name = sentence.get("speaker_name", "Unknown Speaker")
            start_time = sentence.get("start_time", 0)

            # Skip empty sentences
            if not text:
                continue

            # Format timestamp
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"

            # Format speaker name (sanitize for markdown)
            speaker_clean = speaker_name.replace("*", "").replace("_", "\\_")

            # Create formatted line
            formatted_line = f"**{timestamp} {speaker_clean}**: {text}"
            formatted_content.append(formatted_line)

        return "\n\n".join(formatted_content)

    def format_summary(self, summary: Optional[Dict[str, Any]]) -> str:
        """
        Format meeting summary into markdown.

        Args:
            summary: Summary data from API

        Returns:
            Formatted summary content
        """
        if not summary:
            return "No summary available."

        summary_parts = []

        # Action items
        action_items = summary.get("action_items")
        if action_items and isinstance(action_items, str) and action_items.strip():
            summary_parts.append(f"**Action Items:**\n{action_items}")

        # Keywords
        keywords = summary.get("keywords")
        if keywords and isinstance(keywords, str) and keywords.strip():
            summary_parts.append(f"**Keywords:**\n{keywords}")

        # Outline
        outline = summary.get("outline")
        if outline and isinstance(outline, str) and outline.strip():
            summary_parts.append(f"**Outline:**\n{outline}")

        if not summary_parts:
            return "No summary details available."

        return "\n\n".join(summary_parts)

    def create_markdown_content(self, transcript_data: Dict[str, Any]) -> str:
        """
        Create complete markdown content for a transcript.

        Args:
            transcript_data: Complete transcript data from API

        Returns:
            Complete markdown content
        """

        # Extract basic metadata
        title = transcript_data.get("title", "Untitled Meeting")
        organizer_email = transcript_data.get("organizer_email", "Unknown")
        participants = transcript_data.get("participants", [])
        fireflies_users = transcript_data.get("fireflies_users", [])
        duration = transcript_data.get("duration")
        date_string = transcript_data.get("dateString")
        transcript_url = transcript_data.get("transcript_url", "")

        # Format metadata
        formatted_date = self.format_date(date_string)
        formatted_duration = self.format_duration(duration)
        formatted_participants = self.format_participants(participants, fireflies_users)

        # Build markdown content
        markdown_parts = []

        # Title
        markdown_parts.append(f"# {title}")
        markdown_parts.append("")

        # Metadata section
        markdown_parts.append("## Meeting Details")
        markdown_parts.append("")
        markdown_parts.append(f"**Date**: {formatted_date}")
        markdown_parts.append(f"**Duration**: {formatted_duration}")
        markdown_parts.append(f"**Organizer**: {organizer_email}")
        markdown_parts.append(f"**Participants**: {formatted_participants}")

        if transcript_url:
            markdown_parts.append(f"**Fireflies Link**: {transcript_url}")

        markdown_parts.append("")

        # Summary section
        summary = transcript_data.get("summary")
        if summary:
            formatted_summary = self.format_summary(summary)
            markdown_parts.append("## Meeting Summary")
            markdown_parts.append("")
            markdown_parts.append(formatted_summary)
            markdown_parts.append("")

        # Transcript section
        markdown_parts.append("## Transcript")
        markdown_parts.append("")

        sentences = transcript_data.get("sentences", [])
        formatted_transcript = self.format_transcript_sentences(sentences)
        markdown_parts.append(formatted_transcript)

        return "\n".join(markdown_parts)

    def save_transcript(
        self, transcript_data: Dict[str, Any], filename_override: Optional[str] = None
    ) -> Path:
        """
        Save transcript data as a markdown file.

        Args:
            transcript_data: Complete transcript data from API
            filename_override: Custom filename (without extension)

        Returns:
            Path to the saved file

        Raises:
            OSError: If file cannot be saved
        """
        try:
            # Determine filename
            if filename_override:
                filename = filename_override
            else:
                title = transcript_data.get("title", "Untitled Meeting")
                filename = self.sanitize_filename(title)

            # Add .md extension if not present
            if not filename.endswith(".md"):
                filename += ".md"

            # Create file path
            file_path = self.output_directory / filename

            # Handle duplicate filenames
            counter = 1
            original_path = file_path
            while file_path.exists():
                name_without_ext = original_path.stem
                extension = original_path.suffix
                file_path = (
                    self.output_directory / f"{name_without_ext}_{counter}{extension}"
                )
                counter += 1

            # Create markdown content
            markdown_content = self.create_markdown_content(transcript_data)

            # Write file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            self.logger.info(f"Saved transcript: {file_path}")
            return file_path

        except Exception as e:
            self.logger.error(f"Failed to save transcript: {str(e)}")
            raise OSError(f"Could not save transcript file: {str(e)}")

    def get_output_directory(self) -> Path:
        """
        Get the output directory path.

        Returns:
            Path object for the output directory
        """
        return self.output_directory

    def list_saved_transcripts(self) -> List[Path]:
        """
        List all saved transcript files in the output directory.

        Returns:
            List of Path objects for saved transcript files
        """
        try:
            transcript_files = list(self.output_directory.glob("*.md"))
            return sorted(transcript_files)
        except Exception as e:
            self.logger.error(f"Failed to list transcript files: {str(e)}")
            return []

    def get_file_stats(self) -> Dict[str, Any]:
        """
        Get statistics about saved transcript files.

        Returns:
            Dictionary with file statistics
        """
        try:
            files = self.list_saved_transcripts()
            total_size = sum(f.stat().st_size for f in files if f.exists())

            return {
                "total_files": len(files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "files": [f.name for f in files],
            }
        except Exception as e:
            self.logger.error(f"Failed to get file stats: {str(e)}")
            return {
                "total_files": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "files": [],
            }
