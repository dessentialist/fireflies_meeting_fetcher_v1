# Fireflies Meeting Fetcher v1

A Python script to fetch meeting transcripts and details from the Fireflies.ai API and save them as markdown files.

## Project Structure

```
fireflies_meeting_fetcher_v1/
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore patterns
├── config.py                # Configuration management
├── make_lint.py             # Code formatting and linting utilities
├── fireflies_client.py      # API interaction logic (Phase 2)
├── transcript_formatter.py  # Markdown formatting (Phase 3)
├── main.py                  # Main script orchestration (Phase 4)
├── transcripts/             # Output directory for markdown files
└── index.md                 # This documentation file
```

## Core Classes and Functions

### Configuration Module (`config.py`)

#### `Config` Class
- **Purpose**: Centralized configuration management and validation
- **Key Methods**:
  - `__init__()`: Loads and validates environment variables
  - `get_date_range()`: Calculates date range for transcript fetching
  - `get_date_range_iso()`: Returns dates in ISO 8601 format for API calls
  - `_get_required_env()`: Safely retrieves required environment variables
  - `_validate_config()`: Validates all configuration values

#### `setup_logging()` Function
- **Purpose**: Configures application logging with console output
- **Parameters**: `log_level` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Returns**: Configured logger instance

#### `ensure_output_directory()` Function
- **Purpose**: Creates output directory if it doesn't exist
- **Parameters**: `output_dir` - Path to the output directory
- **Error Handling**: Raises OSError if directory creation fails

### Linting Module (`make_lint.py`)

#### `LintFormatter` Class
- **Purpose**: Handles code formatting and linting operations
- **Key Methods**:
  - `format_with_black()`: Formats code using Black formatter
  - `sort_imports_with_isort()`: Sorts imports using isort
  - `lint_with_flake8()`: Lints code using flake8
  - `lint_with_pylint()`: Advanced code analysis with pylint
  - `run_all_formatting()`: Executes all formatting and linting operations
  - `install_dependencies()`: Installs required linting tools

### API Client Module (`fireflies_client.py`)

#### `FirefliesClient` Class
- **Purpose**: Handles all interactions with the Fireflies.ai GraphQL API
- **Key Methods**:
  - `__init__()`: Initialize client with API key and configuration
  - `validate_api_key()`: Test API key validity with a simple query
  - `fetch_transcripts()`: Get list of transcripts within date range
  - `fetch_transcript_details()`: Get detailed transcript content with sentences
  - `fetch_all_transcripts_in_range()`: Handle pagination automatically
  - `test_connection()`: Test API connectivity
  - `_make_graphql_request()`: Core GraphQL request handler with error handling

#### `FirefliesAPIError` Exception
- **Purpose**: Custom exception for API-specific errors
- **Attributes**: `error_code`, `response_data` for debugging

### Data Processing Module (`transcript_formatter.py`)

#### `TranscriptFormatter` Class
- **Purpose**: Converts API responses to formatted markdown files
- **Key Methods**:
  - `__init__()`: Initialize formatter with output directory
  - `sanitize_filename()`: Clean meeting titles for safe filenames
  - `format_duration()`: Convert minutes to human-readable format
  - `format_date()`: Parse ISO 8601 dates to readable format
  - `format_participants()`: Format participant lists intelligently
  - `format_transcript_sentences()`: Convert API sentences to markdown
  - `format_summary()`: Format meeting summaries and action items
  - `create_markdown_content()`: Build complete markdown structure
  - `save_transcript()`: Save formatted content to file with duplicate handling
  - `get_file_stats()`: Get statistics about saved files

### Main Orchestration Module (`main.py`)

#### `FirefliesFetcher` Class
- **Purpose**: Main orchestrator for the entire fetching process
- **Key Methods**:
  - `__init__()`: Initialize fetcher with statistics tracking
  - `initialize()`: Set up all components and validate configuration
  - `fetch_transcript_list()`: Get transcripts in configured date range
  - `process_transcript()`: Process individual transcript (fetch details + save)
  - `process_all_transcripts()`: Process all transcripts with progress tracking
  - `generate_summary_report()`: Create comprehensive operation summary
  - `run()`: Execute complete workflow with error handling

#### Main Functions
- **`main()`**: Entry point with command-line argument handling
- **`print_usage()`**: Display usage information and setup instructions

## Implementation Logic

### Phase 1: Foundation & Setup 
- **Virtual Environment**: Created requirements.txt with all dependencies
- **Configuration Management**: Implemented Config class with validation
- **Logging Setup**: Structured logging with configurable levels
- **Directory Structure**: Created output directory and project organization
- **Code Quality**: Implemented comprehensive linting and formatting utilities

### Phase 2: Core API Client 
- **FirefliesClient Class**: Handles all API interactions with robust error handling
- **Authentication**: Bearer token management and validation with retry logic
- **GraphQL Queries**: Transcripts list and individual transcript fetching
- **Error Handling**: Network errors, rate limiting, and API-specific error handling
- **Date Range Calculation**: Proper handling of 2-month date ranges with pagination

### Phase 3: Data Processing 
- **TranscriptFormatter Class**: Complete markdown conversion and file handling
- **Filename Sanitization**: Safe filename generation from meeting titles with duplicate handling
- **Content Formatting**: Structured markdown with metadata headers and readable transcript
- **File Management**: Output file creation, organization, and statistics tracking

### Phase 4: Main Orchestration 
- **Main Script**: Complete workflow orchestration with progress tracking
- **Progress Tracking**: Real-time progress reporting and comprehensive logging
- **Error Recovery**: Graceful handling of failures with detailed error reporting
- **User Interface**: Clear output, error messages, and summary reports

### Phase 5: Testing & Refinement 
- **Integration Testing**: Validated with real API calls and error scenarios
- **Edge Case Handling**: Empty results, special characters, large files, and API errors
- **Performance Optimization**: Efficient processing with rate limiting and pagination
- **Documentation**: Complete usage examples and troubleshooting information

## API Integration Details

### Fireflies API Structure
- **Base URL**: `https://api.fireflies.ai/graphql`
- **Authentication**: Bearer token in Authorization header
- **Date Format**: ISO 8601 format (`YYYY-MM-DDTHH:mm:ss.sssZ`)
- **Key Queries**:
  - `transcripts`: Fetch list of meetings with metadata
  - `transcript`: Fetch detailed transcript with sentences and speakers

### Expected Data Flow
1. **Configuration Loading**: Load API key and settings from .env
2. **Date Range Calculation**: Generate fromDate and toDate parameters
3. **API Query**: Fetch transcripts list using GraphQL
4. **Detail Fetching**: Get full transcript content for each meeting
5. **Formatting**: Convert to structured markdown format
6. **File Output**: Save each transcript as .md file in transcripts/

### Error Handling Strategy
- **Network Issues**: Exponential backoff and retry logic
- **API Errors**: Clear error messages and graceful degradation
- **File System**: Permission checks and directory creation
- **Data Validation**: Input validation and response verification

## Usage Instructions

### Setup
1. Copy `.env.example` to `.env` and add your Fireflies API key
2. Install dependencies: `pip install -r requirements.txt`
3. Run the script: `python main.py`

### Configuration Options
- `FIREFLIES_API_KEY`: Your Fireflies API key (required)
- `OUTPUT_DIRECTORY`: Directory for output files (default: 'transcripts')
- `MONTHS_TO_FETCH`: Number of months to fetch (default: 2)
- `MAX_TRANSCRIPTS_PER_QUERY`: API query limit (default: 50)

### Code Quality
- Run formatting: `python make_lint.py`
- Check formatting only: `python make_lint.py --check-only`
- Install linting tools: `python make_lint.py --install-deps`

## Design Principles

### Modular Architecture
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Configuration passed in, not hardcoded
- **Error Isolation**: Failures in one transcript don't stop others
- **Clear Interfaces**: Well-defined contracts between modules

### Code Quality Standards
- **Type Hints**: All function parameters and return types
- **Docstrings**: Comprehensive documentation for all public methods
- **Logging**: Structured logging with appropriate levels
- **Validation**: Input validation at module boundaries
- **Testing**: Unit tests for each module (planned)

### Security Considerations
- **API Key Protection**: Never commit API keys to version control
- **Environment Variables**: Secure configuration management
- **Input Validation**: Sanitize all inputs and outputs
- **Error Messages**: Don't expose sensitive information in errors
