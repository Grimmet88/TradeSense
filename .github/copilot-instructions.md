# Copilot Instructions for TradeSense

## Project Overview
TradeSense is a stock trading input application built with Python. The project aims to provide tools and interfaces for analyzing and managing stock trading data.

## Technology Stack
- **Language**: Python 3.x
- **UI Framework**: Streamlit (for interactive web interfaces)
- **Development Environment**: Virtual environment (venv)

## Coding Standards

### Python Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Maximum line length: 88 characters (Black formatter standard)

### Code Organization
- Organize imports in three groups: standard library, third-party, local imports
- Use type hints where appropriate to improve code clarity
- Document functions and classes with docstrings (Google or NumPy style)

### Best Practices
- Handle exceptions gracefully with specific error messages
- Validate user inputs before processing
- Use logging instead of print statements for debugging
- Keep sensitive data (API keys, credentials) in environment variables, never in code

## Testing
- Write unit tests for core business logic
- Use pytest as the testing framework
- Aim for meaningful test coverage, especially for critical trading logic
- Test edge cases and error conditions

## Documentation
- Update README.md when adding new features or changing setup instructions
- Document API endpoints and data formats
- Include examples for complex functionality
- Keep inline comments minimal but meaningful

## Version Control
- Write clear, descriptive commit messages
- Keep commits focused on single changes
- Don't commit sensitive data, virtual environments, or generated files (already in .gitignore)

## Financial Data Handling
- Ensure accuracy in all financial calculations
- Use appropriate data types for monetary values (avoid floating-point precision issues)
- Validate data sources and handle missing or invalid data gracefully
- Consider timezone handling for market data

## Security Considerations
- Never hardcode API keys or credentials
- Sanitize user inputs to prevent injection attacks
- Handle financial data with appropriate security measures
- Follow secure coding practices for financial applications
