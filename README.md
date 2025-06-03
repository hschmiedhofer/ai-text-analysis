# AI-Text-Analysis

A FastAPI-based text analysis service that identifies spelling, grammar, and style errors in submitted text using Google's Gemini AI model.

**Note: This is a demonstration project that uses SQLite for easy setup and testing.**

## Features

- **Text Analysis**: Comprehensive error detection for spelling, grammar, and style issues
- **AI-Powered**: Leverages Google Gemini AI for intelligent text assessment
- **Error Validation**: Advanced position validation and context verification
- **API Authentication**: Secure access with Bearer token authentication
- **Database Storage**: Automatic SQLite database creation for demo purposes
- **RESTful API**: Well-documented endpoints with OpenAPI/Swagger integration
- **Error Handling**: Robust error handling with detailed error categorization

## Requirements

- Python 3.11+
- UV package manager
- Google Gemini API key

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-text-analysis
   ```

2. **Install dependencies with UV**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your actual values:
   ```env
   # Google API Key for Gemini
   GOOGLE_API_KEY=your_actual_gemini_api_key
   # Model ID for Gemini
   GEMINI_MODEL_ID=gemini-2.0-flash
   # API Key for endpoint authentication
   API_KEY=your_demo_api_key
   ```

4. **Start the server**:
   ```bash
   fastapi dev
   ```
   or
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000` and will automatically create an SQLite database on first run.

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Authentication

All endpoints require a Bearer token. Include it in the request header:
```bash
Authorization: Bearer your_api_key_here
```

The Bearer token must match the `API_KEY` value in your `.env` file.

## API Endpoints

### Analyze Text
**POST** `/review/`

Analyzes submitted text for errors and returns detailed assessment.

**Example Request**:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/review/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_api_key' \
  -H 'Content-Type: application/json' \
  -d '"Investing in robust media literacy educasion from an early age are not merely benefiscial, but, in point of fact, esential."'
```

**Response**:
```json
{
  "text_submitted": "Investing in robust media literacy educasion...",
  "summary": "Text quality assessment summary",
  "processing_time": 2.34,
  "tokens_used": 150,
  "created_at": "2025-06-03T10:30:00Z",
  "errors": [
    {
      "text_original": "educasion",
      "text_corrected": "education",
      "category": "spelling",
      "position": 37,
      "description": "Spelling error: 'educasion' should be 'education'",
      "context": "literacy educasion from"
    }
  ]
}
```

**Example Request with Bearer Authentication**:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/review/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer hello' \
  -H 'Content-Type: application/json' \
  -d '"This is a sampl text with erors."'
```

### Get Assessment
**GET** `/review/{assessment_id}`

Retrieves a specific text assessment by its ID.

**Example Request**:
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/review/123' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_api_key'
```

### List All Assessments
**GET** `/review/`

Retrieves all completed text assessments (most recent first).

**Example Request**:
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/review/?limit=50' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_api_key'
```

**Response**:
```json
[
  {
    "text_submitted": "Sample text...",
    "summary": "Analysis summary",
    "processing_time": 1.23,
    "tokens_used": 100,
    "created_at": "2025-06-03T10:30:00Z",
    "errors": [...]
  }
]
```

## Error Categories

The API identifies three types of errors:

- **spelling**: Misspelled words and typos
- **grammar**: Grammatical mistakes and syntax errors  
- **style**: Style improvements and readability suggestions


## Environment Configuration

⚠️ **Important**: You must create a `.env` file based on the provided `.env.example` template.

### Required Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes | `your_actual_gemini_api_key` |
| `GEMINI_MODEL_ID` | Gemini model identifier | Yes | `gemini-2.0-flash` |
| `API_KEY` | Bearer token for API authentication | Yes | `my-api-key` (for demo) |

### Setting up Environment Variables

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values:
   ```bash
   # Google API Key for Gemini
   GOOGLE_API_KEY=your_actual_gemini_api_key
   # Model ID for Gemini  
   GEMINI_MODEL_ID=gemini-1.5-flash
   # API Key for endpoint authentication
   API_KEY=hello
   ```

## Database

This demo project automatically creates and manages an SQLite database:

- **Location**: Local SQLite file created automatically
- **Setup**: No manual database setup required
- **Initialization**: Database tables are created on first application start
- **Purpose**: Stores analysis results for demonstration purposes

## Error Handling

The API provides comprehensive error handling:

- **Rate Limit Exceeded**: When Google API quota is reached
- **Authentication Failed**: Invalid or missing Bearer token
- **Request Timeout**: When requests take too long
- **Network Errors**: Connection issues with Google API
- **Invalid Input**: Malformed requests

## Architecture

```
app/
├── main.py                  # FastAPI application entry point
├── models/
│   ├── __init__.py         # Model exports
│   ├── api_models.py       # Pydantic response models
│   └── db_models.py        # SQLModel database models
├── routers/
│   ├── __init__.py
│   └── review.py           # API route handlers
└── services/
    ├── __init__.py
    ├── converters.py       # DB to API model conversion
    ├── database.py         # Database configuration and setup
    ├── security.py         # Bearer token authentication
    └── text_analysis.py    # Core text analysis logic
    └── text_sanitizer.py   # Input text sanitization module
```

## License

MIT License

Copyright (c) 2025 Heinz Schmiedhofer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

