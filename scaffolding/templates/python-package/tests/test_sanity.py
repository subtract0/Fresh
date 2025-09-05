import logging
import pytest
from {{package}} import hello

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hello():
    try:
        result = hello()
        assert result == "hello from {{package}}"
        logger.info("Test passed: %s", result)
    except AssertionError:
        logger.error("Test failed: expected 'hello from {{package}}', got '%s'", result)
        raise
    except Exception as e:
        logger.exception("An unexpected error occurred: %s", e)
        raise