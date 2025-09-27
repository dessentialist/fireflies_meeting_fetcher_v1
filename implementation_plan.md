# Implementation Plan: Fireflies Transcript Fetcher

## **Core Architecture**
```
fireflies_meeting_fetcher_v1/
├── requirements.txt
├── .env                    # API key and settings
├── fireflies_client.py     # API interaction logic
├── transcript_formatter.py # Markdown formatting
├── main.py                 # Main script orchestration
└── transcripts/           # Output directory
```

## **Key Implementation Considerations**

### **1. Authentication & Security**
- Store API key in `.env` file (never commit to git)
- Validate API key format and handle authentication errors
- Implement proper HTTP headers for GraphQL requests

### **2. Date Range Handling**
- Calculate precise 2-month date range (accounting for different month lengths)
- Handle timezone considerations (Fireflies uses UTC)
- Format dates for GraphQL `fromDate` and `toDate` parameters

### **3. GraphQL Query Construction**
- Fetch transcript metadata: title, date, participants, duration
- Retrieve full transcript content with sentences and speakers
- Handle pagination if needed (though unlikely for 2 months of data)
- Include error handling for malformed responses

### **4. File Processing**
- Sanitize meeting titles for valid filenames (remove special characters, limit length)
- Handle duplicate titles (append timestamp or counter)
- Format transcript content as readable markdown with metadata header
- Create output directory if it doesn't exist

### **5. Error Handling & Resilience**
- Network timeout handling
- API rate limit detection and backoff
- Invalid transcript data handling
- File system permission errors
- Graceful degradation (continue processing other transcripts if one fails)

### **6. Content Formatting**
- Markdown header with meeting metadata
- Structured transcript with speaker names and timestamps
- Preserve original formatting from Fireflies API

## **Phase-wise Development Plan**

### **Phase 1: Foundation & Setup** 
**Objective**: Establish project structure and basic configuration
- [ ] Create virtual environment and install dependencies
- [ ] Create `.env.example` template file
- [ ] Set up logging configuration
- [ ] Create output directory structure

### Phase 2: API interaction
**Objective**: Build robust Fireflies API interaction layer
- [ ] Implement `FirefliesClient` class with authentication
- [ ] Create GraphQL query builder for transcripts
- [ ] Add date range calculation utilities
- [ ] Implement error handling and retry logic

### **Phase 3: Data Processing** 
**Objective**: Transform API responses into usable format
- [ ] Build `TranscriptFormatter` class for markdown conversion
- [ ] Implement filename sanitization logic
- [ ] Create metadata extraction utilities
- [ ] Add content validation and cleaning

### **Phase 4: Main Orchestration** 
**Objective**: Tie everything together with main script
- [ ] Create `main.py` with clear workflow
- [ ] Implement progress tracking and reporting
- [ ] Add comprehensive error handling
- [ ] Create user-friendly output and logging

### **Phase 5: Testing & Refinement**
**Objective**: Validate functionality and handle edge cases
- [ ] Test with real API calls
- [ ] Validate file output format
- [ ] Handle edge cases (empty results, special characters)
- [ ] Performance optimization if needed

## **Script Flow**
1. **Initialize**: Load config from `.env`, validate API key, create output directory
2. **Calculate Date Range**: Generate `fromDate` and `toDate` for GraphQL query
3. **Fetch Transcripts**: Query Fireflies API for transcript metadata and content
4. **Process Each Transcript**: Format content and save as `.md` file
5. **Report Results**: Log summary of successful downloads and any errors

## **Dependencies**
- `requests`: HTTP client for API calls
- `python-dotenv`: Environment variable management
- `pathlib`: Cross-platform file handling
- Built-in modules: `datetime`, `json`, `logging`, `re`

## **Configuration via .env File**
```env
FIREFLIES_API_KEY=your_api_key_here
OUTPUT_DIRECTORY=transcripts
API_BASE_URL=https://api.fireflies.ai/graphql
```

## **Error Scenarios to Handle**
- Invalid API key → Clear error message
- Network connectivity issues → Retry with exponential backoff
- Empty transcript results → Informative logging
- Invalid meeting titles → Sanitize to safe filenames
- File write permissions → Clear error with suggested fix

## **Separation of Concerns & Best Practices**

### **Architecture Principles**
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Configuration passed in, not hardcoded
- **Error Isolation**: Failures in one transcript don't stop others
- **Immutable Data Flow**: Transform data through pipeline stages
- **Clear Interfaces**: Well-defined contracts between modules

### **Module Responsibilities**

#### **`fireflies_client.py`** - API Layer
- **Responsibility**: All Fireflies API interactions
- **Dependencies**: `requests`, `datetime`, `logging`
- **Exports**: `FirefliesClient` class with methods:
  - `authenticate()` - Validate API key
  - `fetch_transcripts()` - Query API with date range
  - `get_transcript_content()` - Fetch individual transcript details
- **Error Handling**: Network errors, API rate limits, authentication failures

#### **`transcript_formatter.py`** - Data Transformation Layer  
- **Responsibility**: Convert API responses to markdown format
- **Dependencies**: `pathlib`, `re`, `datetime`
- **Exports**: `TranscriptFormatter` class with methods:
  - `sanitize_filename()` - Clean meeting titles for file names
  - `format_metadata()` - Create markdown header section
  - `format_transcript()` - Convert sentences to readable format
  - `save_transcript()` - Write formatted content to file
- **Error Handling**: Invalid data, file system errors

#### **`main.py`** - Orchestration Layer
- **Responsibility**: Coordinate the entire process
- **Dependencies**: All other modules, `python-dotenv`, `logging`
- **Functions**:
  - `load_config()` - Load and validate environment variables
  - `setup_logging()` - Configure logging output
  - `main()` - Execute the complete workflow
- **Error Handling**: Configuration errors, overall process failures

### **Design Patterns Applied**
- **Builder Pattern**: For constructing GraphQL queries
- **Strategy Pattern**: For different error handling approaches
- **Factory Pattern**: For creating formatted output files
- **Observer Pattern**: For progress logging and reporting

### **Code Quality Standards**
- **Type Hints**: All function parameters and return types
- **Docstrings**: Comprehensive documentation for all public methods
- **Logging**: Structured logging with appropriate levels
- **Validation**: Input validation at module boundaries
- **Testing**: Unit tests for each module (if time permits)

## **Expected Output Format**
Each transcript will be saved as a markdown file with:
- Meeting metadata header (title, date, participants, duration)
- Formatted transcript with speaker names and timestamps
- Clean, readable structure for easy consumption

### **Sample Output Structure**
```markdown
# Meeting Title

**Date**: 2024-01-15  
**Duration**: 45 minutes  
**Participants**: john@example.com, jane@example.com  
**Organizer**: john@example.com  

## Transcript

**[00:00] John**: Welcome everyone to today's meeting...

**[00:15] Jane**: Thanks John, I'd like to discuss...
```
