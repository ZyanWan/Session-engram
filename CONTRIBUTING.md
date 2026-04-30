# Contributing to Session-Engram

## Development Setup

```bash
git clone https://github.com/ZyanWan/Session-engram.git
cd session-engram
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Style

- Python 3.9+
- Use type hints
- Add docstrings for public functions

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request