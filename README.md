# Editorial Validation API

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
   cd diamir-assignment
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
   GEMINI_MODEL_ID=gemini-1.5-flash
   # API Key for endpoint authentication
   API_KEY=your_demo_api_key
   ```

4. **Start the server**:
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
**POST** `/review/analyze`

Analyzes submitted text for errors and returns detailed assessment.

**Example Request**:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/review/analyze' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer your_api_key' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Investing in robust media literacy educasion from an early age are not merely benefiscial, but, in point of fact, esential. It is required that we must equip citizen'\''s with the critcal thinking skill'\''s to evaluate sources."
  }'
```

**Response**:
```json
{
  "text_submitted": "Investing in robust media literacy educasion...",
  "summary": "Text quality assessment summary",
  "processing_time": 2.34,
  "tokens_used": 150,
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


## Error Categories

The API identifies three types of errors:

- **spelling**: Misspelled words and typos
- **grammar**: Grammatical mistakes and syntax errors  
- **style**: Style improvements and readability suggestions

## Testing

### Manual Testing

Use the included test script:
```bash
uv run python -m app.services.text_analysis
```

This will analyze the sample text in `testdata/faulty_article.txt` and output results to `logs/identified_errors.json`.

### API Testing Examples

```bash
# Test with Bearer authentication
curl -X 'POST' \
  'http://127.0.0.1:8000/review/analyze' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer hello' \
  -H 'Content-Type: application/json' \
  -d '"This is a sampl text with erors."'

# Health check (no auth required)
curl -X GET "http://localhost:8000/health"
```

## Environment Configuration

⚠️ **Important**: You must create a `.env` file based on the provided `.env.example` template.

### Required Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes | `your_actual_gemini_api_key` |
| `GEMINI_MODEL_ID` | Gemini model identifier | Yes | `gemini-1.5-flash` |
| `API_KEY` | Bearer token for API authentication | Yes | `hello` (for demo) |

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
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and setup
├── models/
│   └── models.py        # Pydantic/SQLModel data models
├── routers/
│   └── review.py        # API route handlers
└── services/
    ├── security.py      # Bearer token authentication
    └── text_analysis.py # Core text analysis logic
```

## Advanced Features

### Error Position Validation

The service includes sophisticated error position validation that:
- Finds error context within the original text
- Handles multiple occurrences of the same context
- Validates calculated positions against actual text
- Drops incorrectly positioned errors with detailed logging

### Token Usage Tracking

Each analysis tracks:
- Processing time
- Google API tokens consumed
- Error counts by category
- Text quality summary

## Troubleshooting

### Common Issues

1. **"No GOOGLE_API_KEY found"**: 
   - Ensure you've created a `.env` file from `.env.example`
   - Verify your `.env` file contains a valid Google Gemini API key
   
2. **Authentication failures**: 
   - Verify Bearer token is included in request headers: `Authorization: Bearer your_api_key`
   - Check that the Bearer token matches the `API_KEY` value in your `.env` file

3. **Rate limit errors**: 
   - Check your Google API quota and usage limits
   
4. **Module not found errors**:
   - Ensure you're using `uv run` prefix for Python commands
   - Verify dependencies are installed with `uv sync`

### Demo Setup Validation

Before running the application, ensure:
- `.env` file exists and contains all required variables
- Google API key is valid and has necessary permissions
- Bearer token (`API_KEY`) is set for authentication

### Development with UV

UV provides fast dependency management:

```bash
# Install new dependencies
uv add package_name

# Run the application
uv run uvicorn app.main:app --reload

# Run test scripts
uv run python -m app.services.text_analysis
```

## Demo Usage

This project is designed for demonstration purposes:

1. **Easy Setup**: Automatic SQLite database creation
2. **Simple Auth**: Bearer token authentication for testing
3. **Test Data**: Includes sample text with intentional errors
4. **Immediate Testing**: Start analyzing text right after setup

Perfect for showcasing AI-powered text analysis capabilities!

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]