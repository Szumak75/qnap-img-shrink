# Contributing to QNAP Image Shrink

Thank you for considering contributing to this project!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Szumak75/qnap-img-shrink.git
   cd qnap-img-shrink
   ```

2. Install dependencies:
   ```bash
   poetry install --with dev
   ```

3. Run tests:
   ```bash
   poetry run pytest tests/
   ```

## Code Style

- **Language**: Python 3.11+
- **Formatter**: black (88 characters line length)
- **Linter**: pycodestyle
- **Type hints**: Required for all public functions/methods
- **Docstrings**: Google style, required for all modules/classes/public methods

### Docstring Format

```python
def function_name(arg1: str, arg2: int) -> bool:
    """Short one-line summary.
    
    Optional detailed description.
    
    ### Arguments:
    * arg1: str - Description of arg1.
    * arg2: int - Description of arg2.
    
    ### Returns:
    bool - Description of return value.
    
    ### Raises:
    * ValueError: When condition occurs.
    
    ### Examples:
    ```python
    >>> function_name("test", 42)
    True
    ```
    """
```

## Testing

- Write tests for all new features
- Maintain >80% code coverage
- Use pytest fixtures for setup
- Follow existing test structure

```bash
# Run all tests
poetry run pytest tests/

# Run specific test file
poetry run pytest tests/test_converter.py -v

# Run with coverage
poetry run pytest tests/ --cov=qimgshrink
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Format code: `poetry run black .`
5. Run tests: `poetry run pytest tests/`
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Architecture Guidelines

This project follows jsktoolbox patterns:

- **BData**: All data containers inherit from this
- **ReadOnlyClass**: Use for constant key classes
- **Raise.error()**: Use for structured error handling

Example:
```python
from jsktoolbox.basetool import BData
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise

class _Keys(object, metaclass=ReadOnlyClass):
    """Keys for data storage."""
    VALUE: str = "__value__"

class MyClass(BData):
    """My data class."""
    
    def __init__(self, value: str) -> None:
        self._set_data(key=_Keys.VALUE, value=value, set_default_type=str)
    
    @property
    def value(self) -> str:
        """Get value."""
        tmp = self._get_data(key=_Keys.VALUE)
        if tmp is None:
            raise Raise.error(
                message="Value not set",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp
```

## Questions?

Feel free to open an issue for any questions or suggestions.
