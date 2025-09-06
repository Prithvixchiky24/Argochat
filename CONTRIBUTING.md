# Contributing to ARGO AI - FloatChat Enhanced

Thank you for your interest in contributing to ARGO AI! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Setup](#-development-setup)
- [Contribution Guidelines](#-contribution-guidelines)
- [Pull Request Process](#-pull-request-process)
- [Coding Standards](#-coding-standards)
- [Testing](#-testing)
- [Documentation](#-documentation)

## 🤝 Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git
- Basic understanding of oceanographic data and ARGO floats
- Familiarity with Python data science stack (pandas, numpy, etc.)

### Areas for Contribution

1. **Core Features**
   - Data ingestion improvements
   - New visualization types
   - AI/ML model enhancements
   - Database optimizations

2. **Documentation**
   - API documentation
   - Tutorials and examples
   - User guides
   - Code comments

3. **Testing**
   - Unit tests
   - Integration tests
   - Performance tests
   - Data validation tests

4. **Bug Fixes**
   - Report and fix bugs
   - Performance improvements
   - Security enhancements

## 💻 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/argoai.git
cd argoai

# Add upstream remote
git remote add upstream https://github.com/original/argoai.git
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Configure Environment

```bash
# Copy environment template
cp config/.env.example .env

# Edit .env with your settings
# Add your Google Gemini API key
```

### 4. Verify Setup

```bash
# Run tests
pytest

# Start application
streamlit run app2.py
```

## 📝 Contribution Guidelines

### Issue Reporting

1. **Search existing issues** before creating new ones
2. **Use clear, descriptive titles**
3. **Provide detailed descriptions** including:
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Environment details
   - Screenshots/logs if applicable

### Feature Requests

1. **Check roadmap** and existing feature requests
2. **Describe the problem** you're trying to solve
3. **Propose a solution** with implementation details
4. **Consider backward compatibility**

### Types of Contributions

#### 🐛 Bug Fixes
- Fix reported issues
- Improve error handling
- Optimize performance bottlenecks

#### ✨ New Features
- Add new data visualization types
- Implement new AI models
- Extend database capabilities
- Add export/import functionality

#### 📚 Documentation
- Improve API documentation
- Add code examples
- Write tutorials
- Update README files

#### 🧪 Testing
- Add unit tests
- Improve test coverage
- Add integration tests
- Performance benchmarking

## 🔄 Pull Request Process

### 1. Branch Strategy

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b bugfix/issue-number-description

# For documentation
git checkout -b docs/improvement-description
```

### 2. Development Process

1. **Make your changes**
2. **Add tests** for new functionality
3. **Update documentation** if necessary
4. **Run tests** and ensure they pass
5. **Check code quality** with linting tools

```bash
# Run tests
pytest tests/ -v

# Check code formatting
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
pylint src/

# Type checking
mypy src/
```

### 3. Commit Guidelines

Follow conventional commit format:

```bash
# Format: <type>(<scope>): <description>
git commit -m "feat(visualization): add 3D temperature profile plots"
git commit -m "fix(database): resolve connection timeout issues"
git commit -m "docs(readme): update installation instructions"
```

**Commit Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code formatting
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 4. Submit Pull Request

1. **Push your branch**
```bash
git push origin feature/your-feature-name
```

2. **Create Pull Request** on GitHub
3. **Fill out PR template** completely
4. **Link related issues**
5. **Request review** from maintainers

### 5. PR Requirements

- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Changelog updated (if applicable)
- [ ] No merge conflicts
- [ ] PR description is clear and complete

## 🎨 Coding Standards

### Python Style

Follow [PEP 8](https://pep8.org/) with these specifics:

- **Line length**: 88 characters (Black default)
- **Imports**: Use `isort` for import sorting
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Use type hints for public APIs

### Code Organization

```python
"""Module docstring.

Detailed description of the module's purpose.
"""

import standard_library
import third_party
import local_imports

# Constants
CONSTANT_VALUE = "value"

class ClassName:
    """Class docstring."""
    
    def __init__(self, param: str) -> None:
        """Initialize instance."""
        self.param = param
    
    def public_method(self, arg: int) -> str:
        """Public method docstring.
        
        Args:
            arg: Description of argument.
            
        Returns:
            Description of return value.
            
        Raises:
            ValueError: When argument is invalid.
        """
        return str(arg)
```

### Database Code

```python
# Use SQLAlchemy models
# Follow database naming conventions
# Add proper indexing
# Handle transactions properly

class FloatData(Base):
    """ARGO float data model."""
    __tablename__ = 'float_data'
    
    id = Column(Integer, primary_key=True)
    platform_number = Column(String, nullable=False, index=True)
    # ... other columns
```

### Visualization Code

```python
# Use consistent color schemes
# Add proper axis labels and titles
# Make plots interactive where beneficial
# Support both light and dark themes

def create_temperature_profile(data: pd.DataFrame) -> go.Figure:
    """Create temperature profile visualization.
    
    Args:
        data: DataFrame with temperature and depth data.
        
    Returns:
        Plotly figure object.
    """
    fig = go.Figure()
    # Implementation
    return fig
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_database/
│   ├── test_ai/
│   └── test_visualization/
├── integration/            # Integration tests
├── fixtures/               # Test data
└── conftest.py            # Pytest configuration
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

from src.database.database_manager import DatabaseManager

class TestDatabaseManager:
    """Test database manager functionality."""
    
    @pytest.fixture
    def db_manager(self):
        """Create database manager instance."""
        return DatabaseManager()
    
    def test_connection(self, db_manager):
        """Test database connection."""
        assert db_manager.test_connection()
    
    @patch('src.database.database_manager.create_engine')
    def test_connection_failure(self, mock_engine, db_manager):
        """Test connection failure handling."""
        mock_engine.side_effect = Exception("Connection failed")
        
        with pytest.raises(ConnectionError):
            db_manager.connect()
```

### Test Coverage

Maintain minimum 80% test coverage:

```bash
# Run tests with coverage
pytest --cov=src tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
```

## 📖 Documentation

### API Documentation

Use docstrings for all public APIs:

```python
def process_argo_data(
    data: pd.DataFrame,
    quality_flags: Optional[List[str]] = None,
    depth_range: Optional[Tuple[float, float]] = None
) -> pd.DataFrame:
    """Process ARGO oceanographic data.
    
    This function processes raw ARGO data by applying quality control
    filters and depth range restrictions.
    
    Args:
        data: Raw ARGO data DataFrame with columns:
            - TEMP: Temperature values
            - PSAL: Salinity values
            - PRES: Pressure values
            - QC flags for each parameter
        quality_flags: List of acceptable quality flag values.
            Defaults to ['1', '2'] (good and probably good).
        depth_range: Tuple of (min_depth, max_depth) in meters.
            If None, all depths are included.
    
    Returns:
        Processed DataFrame with filtered data.
        
    Raises:
        ValueError: If required columns are missing.
        TypeError: If data is not a pandas DataFrame.
        
    Example:
        >>> import pandas as pd
        >>> data = pd.DataFrame({
        ...     'TEMP': [15.2, 14.8, 13.5],
        ...     'PSAL': [34.5, 34.7, 35.1],
        ...     'PRES': [10.5, 50.2, 100.8],
        ...     'TEMP_QC': ['1', '1', '2'],
        ...     'PSAL_QC': ['1', '2', '1']
        ... })
        >>> processed = process_argo_data(data, quality_flags=['1'])
        >>> print(len(processed))
        2
    """
```

### README Updates

When adding new features, update relevant sections:

- Features list
- Installation instructions
- Usage examples
- API documentation links

## 🔧 Development Tools

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### IDE Setup

Recommended VS Code extensions:

- Python
- Pylance
- Black Formatter
- GitLens
- Docker

### Debugging

Use debugging tools:

```python
# For development debugging
import pdb; pdb.set_trace()

# For logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

## 🌟 Recognition

Contributors will be recognized in:

- README contributors section
- Release notes
- Project documentation
- Annual contributor reports

## 📞 Getting Help

- **GitHub Discussions**: General questions and discussions
- **Issues**: Bug reports and feature requests  
- **Email**: maintainers@argoai.project
- **Discord**: [Join our community](https://discord.gg/argoai)

## 📝 License

By contributing to ARGO AI, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to ARGO AI! Your efforts help advance oceanographic research and data accessibility. 🌊🤖
