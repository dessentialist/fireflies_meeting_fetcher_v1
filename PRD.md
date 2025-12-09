# Product Requirements Document (PRD)
# Fireflies Meeting Fetcher

**Version:** 1.0  
**Date:** September 27, 2025  
**Author:** Darpan Shah

---

## 📋 Executive Summary

The Fireflies Meeting Fetcher is a Python-based automation tool that extracts meeting transcripts from Fireflies.ai and converts them into well-formatted markdown files. This tool addresses the need for centralized, searchable, and portable meeting documentation.

### Key Value Propositions
- **Automation**: Eliminates manual transcript export processes
- **Standardization**: Consistent markdown format across all meetings
- **Portability**: Local storage for offline access and backup
- **Searchability**: Text-based format enables easy searching and indexing

---

## 🎯 Product Overview

### Vision Statement
To create a seamless bridge between Fireflies.ai's meeting transcription service and local document management, enabling users to maintain comprehensive meeting archives in their preferred format.

### Mission
Provide a reliable, automated solution for extracting and formatting Fireflies.ai meeting transcripts into searchable, portable markdown documents.

---

## 👥 Target Users

### Primary Users
- **Business Professionals**: Regular meeting participants who need meeting documentation
- **Project Managers**: Teams requiring centralized meeting archives
- **Consultants**: Client-facing professionals needing meeting records
- **Remote Teams**: Distributed teams relying on meeting transcripts

### User Personas

#### Persona 1: "Meeting Manager Mary"
- **Role**: Project Manager at a consulting firm
- **Pain Points**: Manually exporting transcripts, inconsistent formats
- **Goals**: Automated, standardized meeting documentation
- **Technical Level**: Intermediate

#### Persona 2: "Developer Dave"
- **Role**: Software Engineer in a remote team
- **Pain Points**: Need for searchable meeting history, offline access
- **Goals**: Local storage, version control integration
- **Technical Level**: Advanced

---

## 🎯 Goals & Objectives

### Primary Goals
1. **Automate Transcript Export**: Eliminate manual Fireflies.ai transcript downloads
2. **Standardize Format**: Provide consistent markdown formatting across all meetings
3. **Ensure Reliability**: 99%+ success rate for transcript processing
4. **Maintain Performance**: Process 50+ transcripts in under 2 minutes

### Success Metrics
- **Adoption Rate**: Number of active users within 30 days
- **Processing Success**: Percentage of successfully processed transcripts
- **User Satisfaction**: Feedback scores on output quality
- **Time Savings**: Reduction in manual transcript management time

---

## 🔧 Functional Requirements

### Core Features

#### FR-001: API Integration
- **Description**: Connect to Fireflies.ai GraphQL API
- **Acceptance Criteria**:
  - Authenticate using API key
  - Handle rate limiting and retries
  - Support pagination for large transcript sets
- **Priority**: P0 (Critical)

#### FR-002: Transcript Fetching
- **Description**: Retrieve meeting transcripts within specified date range
- **Acceptance Criteria**:
  - Fetch transcripts from last N months (configurable)
  - Handle API errors gracefully
  - Support incremental updates
- **Priority**: P0 (Critical)

#### FR-003: Markdown Formatting
- **Description**: Convert transcript data to well-formatted markdown
- **Acceptance Criteria**:
  - Include meeting metadata (date, duration, participants)
  - Format transcript with timestamps and speaker identification
  - Include action items and summaries
  - Sanitize filenames for cross-platform compatibility
- **Priority**: P0 (Critical)

#### FR-004: File Management
- **Description**: Save and organize transcript files
- **Acceptance Criteria**:
  - Create output directory structure
  - Handle duplicate filenames
  - Provide file statistics and reporting
- **Priority**: P0 (Critical)

#### FR-005: Configuration Management
- **Description**: User-configurable settings
- **Acceptance Criteria**:
  - Environment variable support
  - Configurable date ranges
  - Customizable output directories
- **Priority**: P1 (High)

#### FR-006: Progress Reporting
- **Description**: Real-time progress updates and summary reports
- **Acceptance Criteria**:
  - Show processing progress
  - Display success/failure statistics
  - Provide execution time metrics
- **Priority**: P1 (High)

### Advanced Features

#### FR-007: Error Handling & Recovery
- **Description**: Robust error handling and recovery mechanisms
- **Acceptance Criteria**:
  - Retry failed API calls
  - Log detailed error information
  - Continue processing after individual failures
- **Priority**: P1 (High)

#### FR-008: Logging & Debugging
- **Description**: Comprehensive logging for troubleshooting
- **Acceptance Criteria**:
  - Configurable log levels
  - Detailed API request/response logging
  - Performance metrics tracking
- **Priority**: P2 (Medium)

---

## 🚫 Non-Functional Requirements

### Performance Requirements
- **Processing Speed**: Process 50 transcripts in under 2 minutes
- **Memory Usage**: Maximum 100MB RAM usage
- **API Efficiency**: Respect Fireflies.ai rate limits (50 requests/minute)

### Reliability Requirements
- **Success Rate**: 99%+ successful transcript processing
- **Error Recovery**: Automatic retry for transient failures
- **Data Integrity**: Ensure complete transcript data extraction

### Usability Requirements
- **Setup Time**: Complete setup in under 5 minutes
- **Documentation**: Clear installation and usage instructions
- **Error Messages**: User-friendly error descriptions

### Security Requirements
- **API Key Protection**: Secure storage of authentication credentials
- **Data Privacy**: No local storage of sensitive meeting content beyond transcripts
- **Access Control**: Respect Fireflies.ai permission model

### Compatibility Requirements
- **Python Version**: Support Python 3.8+
- **Operating Systems**: Windows, macOS, Linux
- **File Systems**: Cross-platform filename compatibility

---

## 🏗️ Technical Architecture

### System Components

#### 1. Main Orchestrator (`main.py`)
- **Responsibility**: Application entry point and workflow coordination
- **Key Functions**:
  - Initialize components
  - Coordinate transcript processing
  - Generate summary reports

#### 2. API Client (`fireflies_client.py`)
- **Responsibility**: Fireflies.ai GraphQL API interaction
- **Key Functions**:
  - Authentication and session management
  - GraphQL query execution
  - Error handling and retries

#### 3. Transcript Formatter (`transcript_formatter.py`)
- **Responsibility**: Data transformation and file generation
- **Key Functions**:
  - Markdown content generation
  - File naming and organization
  - Metadata extraction

#### 4. Configuration Manager (`config.py`)
- **Responsibility**: Settings and environment management
- **Key Functions**:
  - Environment variable loading
  - Configuration validation
  - Default value management

### Data Flow

```
1. Configuration Loading → 2. API Authentication → 3. Transcript List Fetching
                                                           ↓
8. Summary Report ← 7. File Statistics ← 6. Markdown Generation ← 5. Detailed Transcript Fetching
```

### Technology Stack
- **Language**: Python 3.8+
- **HTTP Client**: Requests library
- **Configuration**: python-dotenv
- **File Handling**: pathlib2
- **Code Quality**: Black, isort, flake8, pylint

---

## 📊 Data Model

### Transcript Data Structure
```python
{
    "id": "string",
    "title": "string",
    "organizer_email": "string",
    "participants": ["string"],
    "fireflies_users": ["string"],
    "duration": "number",
    "dateString": "ISO8601",
    "transcript_url": "string",
    "speakers": [{"id": "string", "name": "string"}],
    "sentences": [{
        "text": "string",
        "speaker_name": "string",
        "start_time": "number",
        "end_time": "number"
    }],
    "summary": {
        "action_items": "string",
        "keywords": "string",
        "outline": "string"
    }
}
```

### Configuration Schema
```python
{
    "api_key": "string (required)",
    "output_directory": "string (default: 'transcripts')",
    "months_to_fetch": "integer (default: 2)",
    "max_transcripts_per_query": "integer (default: 50)"
}
```

---

## 🧪 Testing Strategy

### Unit Testing
- **API Client**: Mock GraphQL responses, test error handling
- **Formatter**: Test markdown generation with various data inputs
- **Configuration**: Test validation and default value handling

### Integration Testing
- **End-to-End**: Full workflow testing with real API (sandbox)
- **File System**: Test file creation and organization
- **Error Scenarios**: Test network failures, API errors

### Performance Testing
- **Load Testing**: Process large numbers of transcripts
- **Memory Profiling**: Monitor resource usage
- **API Rate Limiting**: Test respect for Fireflies.ai limits

---

## 🚀 Implementation Phases

### Phase 1: Core Functionality ✅
- [x] Basic API integration
- [x] Transcript fetching
- [x] Markdown formatting
- [x] File management
- [x] Configuration system

### Phase 2: Enhancement (Future)
- [ ] Incremental updates
- [ ] Duplicate detection
- [ ] Export formats (PDF, Word)
- [ ] Search functionality
- [ ] Web interface

### Phase 3: Advanced Features (Future)
- [ ] Scheduled execution
- [ ] Email notifications
- [ ] Team collaboration features
- [ ] Analytics dashboard

---



## 🔄 Maintenance & Support

### Ongoing Responsibilities
- **API Compatibility**: Monitor Fireflies.ai API changes
- **Bug Fixes**: Address user-reported issues
- **Performance Optimization**: Continuous improvement
- **Documentation Updates**: Keep guides current


---

## 📝 Appendices

### A. API Documentation References
- [Fireflies.ai GraphQL API](https://docs.fireflies.ai/)
- [GraphQL Schema Documentation](https://docs.fireflies.ai/schema/)

### B. Development Standards
- **Code Style**: PEP 8 compliance via Black formatter
- **Import Organization**: isort for import sorting
- **Linting**: flake8 and pylint for code quality
- **Testing**: pytest for unit and integration tests

### C. Deployment Considerations
- **Environment**: Python virtual environment recommended
- **Dependencies**: Managed via requirements.txt
- **Configuration**: Environment variables for sensitive data
- **Monitoring**: Logging for operational visibility

