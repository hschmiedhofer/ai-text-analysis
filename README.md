
# Editorial Validation API

## Task

AI - Developer
Application Task
### Preamble

At our company, we develop modern backend services using Python with a strong focus on type safety and clean architecture. We emphasize well-structured code with Pydantic for data validation and schema definition. We value type annotations throughout the codebase and properly structured data models that ensure reliability and maintainability.

### Basetask

Please create a simple FastAPI backend service that provides an editorial text review functionality. The service should:

1. Expose an API endpoint that accepts a news article text and returns grammar and style suggestions
2. Implement a service that analyzes the submitted text for at least two types of errors:
	- Spelling and grammar mistakes
	- Style issues (e.g., passive voice, wordiness)
3. Use Pydantic for request/response validation with proper type annotations
4. Return a structured response that includes:
	- List of detected errors with their type, position
	- Overall score or summary of the text quality
	- Processing metadata (token count, processing time)

### Technical requirements

- Use FastAPI with Pydantic Models and Pydantic Ai
- Document your API with OpenAPI/Swagger

Think about best practices and how to deliver a structured clean code.

### Extension

Extend your solution to include:
1. API key authentication for endpoint access
2. Ability to save analysis results to a simple database

### Submission

Please submit your solution as a GitHub repository (link) with:
- Complete source code
- README with setup and usage instructions
- Requirements file or modern Python dependency management (uv or poetry)

We value clean, maintainable code with good documentation over complex implementations. Focus on demonstrating your understanding of Python backend development best practices, API design, and data validation.


## Info

Start dev testing via `fastapi dev`