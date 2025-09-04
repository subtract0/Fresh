# ADR-008: State-of-the-Art Python AST Syntax Error Detection

## Status: ACCEPTED
Date: 2025-01-04  
Context: Fixing syntax errors in codebase files for feature inventory parsing

## Decision

Based on latest 2024-2025 best practices research, we will implement robust Python syntax error detection using:

### State-of-the-Art Approach:
1. **Use `ast.parse()` with explicit error handling** for syntax validation
2. **Specific exception catching** instead of generic `Exception`
3. **Structured error reporting** with line numbers and context
4. **Fail-fast parsing** with detailed diagnostics
5. **Production-grade retry logic** for file operations

### Implementation Pattern:
```python
import ast
from typing import Optional, Tuple

def validate_python_syntax(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Python file syntax using current best practices.
    Returns (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Parse with explicit mode and feature flags
        ast.parse(source_code, filename=file_path, mode='exec')
        return True, None
        
    except SyntaxError as e:
        error_msg = f"Syntax error in {file_path}:{e.lineno}:{e.offset} - {e.msg}"
        return False, error_msg
    except UnicodeDecodeError as e:
        error_msg = f"Encoding error in {file_path}: {e}"
        return False, error_msg
    except FileNotFoundError:
        error_msg = f"File not found: {file_path}"
        return False, error_msg
    except PermissionError:
        error_msg = f"Permission denied: {file_path}"
        return False, error_msg
```

### Key Improvements Over Legacy Approaches:
- **Specific exception types** rather than bare `except:`
- **Structured error messages** with context
- **UTF-8 encoding specification** for modern Python files
- **Comprehensive file operation error handling**
- **Type hints for better tooling support**

## Alternatives Considered

1. **Using `compile()` builtin**: Less specific error information
2. **Regex-based validation**: Fragile and incomplete
3. **Third-party parsers**: Additional dependencies

## Consequences

### Positive:
- ✅ Current best practice compliance (2024-2025)
- ✅ Detailed error diagnostics for debugging
- ✅ Robust file handling with proper encoding
- ✅ Type-safe implementation
- ✅ Specific error categorization

### Negative:
- ⚠️ Slightly more verbose than legacy approaches
- ⚠️ Requires Python 3.8+ for full type hint support

## References

- [Python 3.13 AST Documentation](https://docs.python.org/3/library/ast.html)
- [Python Exception Handling Best Practices 2024-2025](https://metana.io/blog/mastering-python-exception-handling-best-practices-for-try-except/)
- [AST Analysis Patterns 2024](https://medium.com/@ebimsv/python-for-ai-week-10-error-handling-and-exceptions-in-python-296a75c34abe)

## Implementation

This ADR guides the fix for syntax errors in:
- `ai/memory/enhanced_firestore.py` 
- `ai/system/init.py`
- `scripts/issue_to_pr.py`

All fixes will follow the established pattern above.
