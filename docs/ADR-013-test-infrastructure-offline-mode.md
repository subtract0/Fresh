# ADR-013: Test Infrastructure Offline Mode Implementation

**Date**: 2025-01-05  
**Status**: Accepted  
**Context**: Broken Windows Repair Initiative  
**Related**: ADR-012 (Enhanced Agent Orchestration)  

## Context

During autonomous system assessment, we discovered critical broken windows in the test infrastructure:

- 11 MotherAgent tests failing due to timeout issues
- 1 TechnicalAssessmentAgent test failing due to mocking issues  
- Tests making real OpenAI API calls instead of running offline
- No consistent test configuration across the project

This violated our No Broken Windows policy and prevented confident development.

## Decision

Implement comprehensive offline mode testing infrastructure:

### 1. **Offline Mode Enforcement**
- All tests must respect `FRESH_OFFLINE=1` environment variable
- Leverage existing `is_offline()` utility function in `ai/utils/settings.py`
- Tests default to offline when `OPENAI_API_KEY` not configured

### 2. **Test Configuration Standardization**
- Added `pytest.ini` with proper timeout settings (5s default)
- Standardized test discovery patterns and markers
- Configured thread-based timeout handling

### 3. **Mock Strategy Improvements**
- Fixed complex pathlib mocking in research agent tests
- Simplified mocking by mocking higher-level methods instead of filesystem operations
- Ensured all external API calls are properly mocked

### 4. **Safety Mechanisms**
```python
def is_offline() -> bool:
    """Return True when offline/safe mode is requested."""
    val = os.getenv("FRESH_OFFLINE", "").strip().lower()
    if val in _TRUE_SET:
        return True
    # If no OpenAI key is configured, stay offline by default
    if not os.getenv("OPENAI_API_KEY"):
        return True
    return False
```

## Implementation

### Files Modified:
- `pytest.ini` - New test configuration  
- `tests/test_enhanced_orchestration.py` - Fixed pathlib mocking
- Existing `ai/utils/settings.py` - Leveraged offline detection
- All tests now run with `FRESH_OFFLINE=1` in CI/CD

### Results:
- ✅ **303 tests passing, 7 skipped** (expected Firestore skips)
- ✅ **Zero broken windows remaining**
- ✅ **Sub-5-second test execution** 
- ✅ **No external API calls during testing**

## Consequences

### Positive:
- **Reliable CI/CD**: Tests are deterministic and fast
- **Developer Productivity**: No API keys needed for testing
- **Cost Savings**: No accidental API usage during development
- **System Integrity**: Can verify system health at any time

### Trade-offs:
- Some tests skip real integration testing (by design)
- Developers must manually test with real APIs when needed
- Requires discipline to maintain offline/online mode separation

## Validation

```bash
# All tests pass in offline mode
FRESH_OFFLINE=1 poetry run pytest -q
# Result: 303 passed, 7 skipped

# System remains stable
poetry run python -m ai.cli.fresh scan . --json
# Result: 38 issues identified (mostly test data)

# Feature inventory works cleanly
poetry run python -m ai.cli.fresh feature inventory
# Result: 577 features catalogued without parsing errors
```

## Future Considerations

1. **Integration Test Suite**: Add separate integration tests for real API validation
2. **Performance Monitoring**: Track test execution times to catch regressions
3. **Mocking Library**: Consider standardizing on specific mocking patterns
4. **CI/CD Enhancement**: Add test result reporting and trends

## References

- **No Broken Windows Policy**: Martin Fowler's Clean Code principles
- **Test Pyramid**: Unit tests should be fast, reliable, and isolated
- **Fail Fast**: Tests should fail quickly to enable rapid feedback
- **Safety First**: Better to skip a test than break the build

---

*This ADR documents the critical infrastructure fix that restored system integrity and enabled confident autonomous development.*
