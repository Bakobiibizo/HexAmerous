import pytest
from src.helpers.log_helper import Log

@pytest.fixture
def logger():
    return Log()

# Happy path tests
@pytest.mark.parametrize(
    "level, variable_dict, expected_output",
    [
        ("DEBUG", {"key1": "value1", "key2": "value2"}, "\nkey1 - value1\nkey2 - value2\n"),
        ("INFO", "Some info message", "Some info message\n"),
        ("WARNING", "Some warning message", "Some warning message\n"),
        ("ERROR", "Some error message", "Some error message\n"),
        ("CRITICAL", "Some critical message", "Some critical message\n"),
        ("EXCEPTION", "Some exception message", "Some exception message\n"),
    ],
    ids=[
        "debug_level_with_variable_dict",
        "info_level_with_string",
        "warning_level_with_string",
        "error_level_with_string",
        "critical_level_with_string",
        "exception_level_with_string",
    ]
)
def test_log_functions(logger, level, variable_dict, expected_output):
    logger.level = level
    logger.log(variable_dict)
    logger.debug(expected_output)

# Edge cases
@pytest.mark.parametrize(
    "level, variable_dict, expected_output",
    [
        ("DEBUG", {}, "\n"),
        ("INFO", "", "\n"),
        ("WARNING", None, ""),
        ("ERROR", "Some error message", "Some error message\n"),
        ("CRITICAL", "Some critical message", "Some critical message\n"),
        ("EXCEPTION", "Some exception message", "Some exception message\n"),
    ],
    ids=[
        "debug_level_with_empty_variable_dict",
        "info_level_with_empty_string",
        "warning_level_with_none",
        "error_level_with_string",
        "critical_level_with_string",
        "exception_level_with_string",
    ]
)
def test_edge_cases(logger, level, variable_dict, expected_output):
    logger.level = level
    logger.log(variable_dict)
    logger.debug(expected_output)

# Error cases
@pytest.mark.parametrize(
    "level, variable_dict, expected_output",
    [
        ("INVALID", {"key1": "value1", "key2": "value2"}, "\nkey1 - value1\nkey2 - value2\n"),
        ("DEBUG", 123, ""),
        ("INFO", ["Some info message"], ""),
        ("WARNING", {"key1": "value1", "key2": "value2"}, ""),
        ("ERROR", {"key1": "value1", "key2": "value2"}, ""),
        ("CRITICAL", {"key1": "value1", "key2": "value2"}, ""),
        ("EXCEPTION", {"key1": "value1", "key2": "value2"}, ""),
    ],
    ids=[
        "invalid_log_level",
        "debug_level_with_invalid_variable_dict",
        "info_level_with_invalid_string",
        "warning_level_with_dict",
        "error_level_with_dict",
        "critical_level_with_dict",
        "exception_level_with_dict",
    ]
)
def test_error_cases(logger, level, variable_dict, expected_output):
    logger.level = level
    logger.log(variable_dict)
    logger.debug
