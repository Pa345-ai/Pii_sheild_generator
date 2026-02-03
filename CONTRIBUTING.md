# Contributing to PII-Shield Engine

Thank you for your interest in contributing to PII-Shield Engine! This document provides guidelines for development, testing, and contributing to the project.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Docker (optional, for container testing)
- Virtual environment tool (venv, virtualenv, or conda)

### Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pii-shield-engine
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify installation**
   ```bash
   python demo.py
   pytest tests/ -v
   ```

## Project Structure

```
pii-shield-engine/
├── pii_shield/          # Core detection engine
│   ├── detector.py      # Main detection logic
│   ├── patterns.py      # PII pattern definitions
│   ├── validator.py     # Validation logic
│   ├── masking.py       # Masking strategies
│   └── utils.py         # Utility functions
├── api/                 # FastAPI application
│   ├── main.py          # API endpoints
│   └── schemas.py       # Pydantic models
├── config/              # Configuration management
│   └── settings.py      # Settings with environment support
├── tests/               # Test suite
│   ├── test_detector.py
│   ├── test_masking.py
│   └── test_validator.py
└── docs/                # Documentation (if needed)
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

Follow the coding standards below when making changes.

### 3. Run Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_detector.py -v

# Run with coverage
make test-cov
```

### 4. Format Code

```bash
# Format with black
make format

# Or manually
black pii_shield/ api/ tests/
```

### 5. Lint Code

```bash
# Run linters
make lint

# Or manually
flake8 pii_shield/ api/ tests/
mypy pii_shield/ api/
```

### 6. Commit Changes

```bash
git add .
git commit -m "feat: add new PII type for driver licenses"
```

Use conventional commit messages:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Build process or auxiliary tool changes

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub/GitLab.

## Coding Standards

### Python Style

- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 88 characters (Black default)
- Use docstrings for all public functions and classes

### Example Function

```python
def detect_credit_cards(
    text: str,
    confidence_threshold: float = 0.9
) -> List[PIIMatch]:
    """
    Detect credit card numbers in text.
    
    Args:
        text: Input text to scan
        confidence_threshold: Minimum confidence score (0.0-1.0)
        
    Returns:
        List of PIIMatch objects for detected credit cards
        
    Raises:
        ValueError: If confidence_threshold is not in range [0.0, 1.0]
    """
    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError("Confidence threshold must be between 0 and 1")
    
    # Implementation here
    pass
```

### Documentation

- Use Google-style docstrings
- Include examples for complex functions
- Keep docstrings concise but complete
- Update README.md when adding major features

## Testing Guidelines

### Writing Tests

1. **Test Organization**
   - One test file per module
   - Group related tests in classes
   - Use descriptive test names

2. **Test Structure**
   ```python
   class TestCreditCardDetection:
       """Test credit card detection functionality"""
       
       def setup_method(self):
           """Setup run before each test method"""
           self.detector = PIIDetector()
       
       def test_valid_visa_card(self):
           """Test detection of valid Visa card"""
           text = "Card: 4532-1488-0343-6467"
           matches = self.detector.detect_all(text)
           
           assert len(matches) > 0
           assert matches[0].pii_type == PIIType.CREDIT_CARD.value
   ```

3. **Test Coverage**
   - Aim for >90% code coverage
   - Test happy paths and edge cases
   - Test error handling
   - Include performance tests for critical paths

4. **Running Tests**
   ```bash
   # All tests
   pytest tests/ -v
   
   # Specific test class
   pytest tests/test_detector.py::TestCreditCardDetection -v
   
   # Specific test
   pytest tests/test_detector.py::TestCreditCardDetection::test_valid_visa_card -v
   
   # With coverage
   pytest tests/ --cov=pii_shield --cov-report=html
   ```

## Adding New PII Types

To add a new PII type:

1. **Update patterns.py**
   ```python
   class PIIType(Enum):
       # ... existing types ...
       MY_NEW_TYPE = "MY_NEW_TYPE"
   ```

2. **Add pattern definition**
   ```python
   PIIPattern(
       pii_type=PIIType.MY_NEW_TYPE,
       pattern=r'your-regex-pattern',
       confidence=0.85,
       description="Description of new PII type",
       requires_validation=True  # if validation needed
   )
   ```

3. **Add validation (if needed)**
   In `validator.py`:
   ```python
   @staticmethod
   def validate_my_new_type(value: str) -> bool:
       """Validate new PII type"""
       # Validation logic
       return True
   ```

4. **Add masking logic**
   In `masking.py`:
   ```python
   def _mask_my_new_type(self, value: str) -> str:
       """Mask new PII type"""
       # Masking logic
       return masked_value
   ```

5. **Write tests**
   Create tests in `tests/test_detector.py`:
   ```python
   class TestMyNewTypeDetection:
       def test_detect_my_new_type(self):
           # Test implementation
           pass
   ```

6. **Update documentation**
   - Add to README.md supported types table
   - Update API documentation
   - Add examples

## Performance Considerations

### Guidelines

1. **Avoid unnecessary regex compilations**
   - Compile patterns once at initialization
   - Reuse compiled patterns

2. **Minimize string operations**
   - Use slicing instead of concatenation in loops
   - Use join() for building strings from lists

3. **Optimize hot paths**
   - Profile code to identify bottlenecks
   - Use `time.time()` for basic timing
   - Consider caching for expensive operations

4. **Memory efficiency**
   - Don't load entire files into memory
   - Use generators for large datasets
   - Clean up temporary data

### Performance Testing

```python
def test_detection_performance(self):
    """Test detection performance on large text"""
    import time
    
    detector = PIIDetector()
    text = "test data" * 10000
    
    start = time.time()
    matches = detector.detect_all(text)
    elapsed = time.time() - start
    
    assert elapsed < 1.0  # Should complete in < 1 second
```

## Security Considerations

### Guidelines

1. **Never log PII values**
   - Log only metadata (counts, types, positions)
   - Use sanitization before logging

2. **Validate all inputs**
   - Use Pydantic for API validation
   - Check bounds and types

3. **Secure defaults**
   - Enable strict validation by default
   - Use safe masking strategies

4. **Dependencies**
   - Keep dependencies minimal
   - Review security advisories
   - Update regularly

## Documentation

### Code Documentation

- Use docstrings for all public APIs
- Include type hints
- Provide examples for complex functions

### API Documentation

- FastAPI auto-generates docs
- Add descriptions to endpoints
- Include request/response examples
- Document error codes

### User Documentation

- Keep README.md up to date
- Add tutorials for common use cases
- Include deployment guides
- Maintain changelog

## Release Process

### Version Numbering

Follow Semantic Versioning (semver):
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Checklist

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Update documentation
5. Create git tag
6. Build Docker image
7. Create release notes

## Getting Help

### Resources

- **Documentation**: See README.md
- **Issues**: GitHub/GitLab Issues
- **Discussions**: GitHub Discussions
- **Email**: support@pii-shield.example.com

### Reporting Bugs

When reporting bugs, include:
1. Python version
2. Operating system
3. Steps to reproduce
4. Expected behavior
5. Actual behavior
6. Error messages/logs

### Suggesting Features

When suggesting features:
1. Describe the use case
2. Explain expected behavior
3. Provide examples
4. Consider implementation complexity

## Code Review Process

### What Reviewers Look For

1. **Correctness**
   - Does it work as intended?
   - Are edge cases handled?
   - Are there tests?

2. **Code Quality**
   - Is it readable?
   - Is it maintainable?
   - Does it follow standards?

3. **Performance**
   - Are there bottlenecks?
   - Is it efficient?
   - Does it scale?

4. **Security**
   - Are inputs validated?
   - Is PII handled safely?
   - Are there vulnerabilities?

### Review Guidelines

- Be respectful and constructive
- Focus on the code, not the person
- Explain the "why" behind suggestions
- Approve when ready, request changes when needed

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (Commercial License).

---

Thank you for contributing to PII-Shield Engine!
