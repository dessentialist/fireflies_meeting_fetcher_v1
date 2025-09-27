# 🔥 Fireflies Meeting Fetcher

A Python script that automatically fetches meeting transcripts from Fireflies.ai and saves them as well-formatted markdown files.

## ✨ Features

- **Automated Fetching**: Retrieves meeting transcripts from the last 2 months (configurable)
- **Markdown Export**: Saves transcripts as beautifully formatted markdown files
- **Complete Metadata**: Includes meeting details, participants, summaries, and full transcripts
- **Smart File Naming**: Sanitizes meeting titles for valid filenames
- **Progress Tracking**: Real-time progress updates and comprehensive summary reports
- **Error Handling**: Robust error handling with detailed logging
- **Rate Limiting**: Respectful API usage with built-in delays

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Fireflies.ai API key
- Virtual environment (recommended)

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd fireflies_meeting_fetcher_v1
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your FIREFLIES_API_KEY
   ```

3. **Run the fetcher**:
   ```bash
   python main.py
   ```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Required
FIREFLIES_API_KEY=your_api_key_here

# Optional (with defaults)
OUTPUT_DIRECTORY=transcripts
MONTHS_TO_FETCH=2
MAX_TRANSCRIPTS_PER_QUERY=50
```

## 📁 Output

Transcripts are saved as markdown files in the `transcripts/` directory with:

- **Meeting Details**: Date, duration, organizer, participants
- **Summary**: Action items, keywords, outline
- **Full Transcript**: Timestamped conversation with speaker identification
- **Fireflies Link**: Direct link to the original transcript

### Example Output Structure

```
transcripts/
├──meeting_1.md
└── ...
```

## 🛠️ Usage

### Basic Usage
```bash
python main.py
```

### Help
```bash
python main.py --help
```

### Development
```bash
# Format and lint code
python make_lint.py

# Run with debug logging
# Edit main.py to change logging level to "DEBUG"
```

## 📊 Sample Output

```
📊 FIReflies Meeting Fetcher - Summary Report
============================================================
📊 Total transcripts found: 9
📊 Successfully downloaded: 9
📊 Failed downloads: 0
📊 Success rate: 100.0%
📊 Total time: 41.9 seconds
📊 Files in output directory: 9
📊 Total size: 0.53 MB
============================================================
```

## 🏗️ Architecture

- **`main.py`**: Main orchestrator and CLI interface
- **`fireflies_client.py`**: GraphQL API client with retry logic
- **`transcript_formatter.py`**: Markdown formatting and file management
- **`config.py`**: Configuration management and validation
- **`make_lint.py`**: Code formatting and linting utilities

## 🔧 Dependencies

- `requests`: HTTP client for API calls
- `python-dotenv`: Environment variable management
- `pathlib2`: Enhanced path handling

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `python make_lint.py` to ensure code quality
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the [Fireflies.ai API documentation](https://docs.fireflies.ai/)
- Review the `index.md` file for detailed implementation notes
- Open an issue in this repository

---

**Happy meeting transcription! 🎉**
