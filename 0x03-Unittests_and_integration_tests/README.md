# 0x03. Unittests and integration tests

This project contains unit tests and integration tests for Python modules using the `unittest` framework, mocking, and parameterized testing.

## Learning Objectives

By the end of this project, you should understand:

- The difference between unit and integration tests
- Common testing patterns such as mocking, parametrizations and fixtures
- How to use `unittest.mock` to mock external dependencies
- How to write parameterized tests using the `parameterized` library
- How to test properties and memoized functions
- How to write integration tests with proper setup and teardown

## Project Structure

```
0x03-Unittests_and_integration_tests/
├── README.md
├── utils.py
├── client.py
├── fixtures.py
├── test_utils.py
└── test_client.py
```

## Files Description

### Core Modules

- **utils.py**: Contains utility functions including:
  - `access_nested_map()`: Access nested dictionaries with key paths
  - `get_json()`: Fetch JSON data from URLs
  - `memoize`: Decorator for caching function results

- **client.py**: Contains the `GithubOrgClient` class for interacting with GitHub's API:
  - `org`: Property to get organization information
  - `public_repos()`: Method to get public repositories
  - `has_license()`: Static method to check repository licenses

- **fixtures.py**: Contains test fixtures for integration tests

### Test Modules

- **test_utils.py**: Unit tests for the utils module
  - `TestAccessNestedMap`: Tests for `access_nested_map` function
  - `TestGetJson`: Tests for `get_json` function with mocked HTTP calls
  - `TestMemoize`: Tests for the `memoize` decorator

- **test_client.py**: Unit and integration tests for the client module
  - `TestGithubOrgClient`: Unit tests with mocking
  - `TestIntegrationGithubOrgClient`: Integration tests with fixtures

## Running Tests

Execute all tests in a specific file:
```bash
python -m unittest test_utils.py
python -m unittest test_client.py
```

Execute all tests:
```bash
python -m unittest discover
```

Execute tests with verbose output:
```bash
python -m unittest test_utils.py -v
```

## Key Testing Concepts Demonstrated

### Unit Testing
- Testing individual functions in isolation
- Mocking external dependencies (HTTP calls, database calls)
- Parameterized tests for multiple input scenarios
- Exception testing with `assertRaises`

### Integration Testing
- Testing complete workflows end-to-end
- Using fixtures for test data
- Class-level setup and teardown methods
- Mocking only external API calls, not internal logic

### Mocking Patterns
- Using `@patch` as decorator and context manager
- Mocking properties with `PropertyMock`
- Using `side_effect` for complex mock behaviors
- Asserting mock calls and call counts

### Parameterized Testing
- Using `@parameterized.expand` for multiple test cases
- Using `@parameterized_class` for class-level parameterization
- Testing both positive and negative cases

## Requirements

- Python 3.7+
- Ubuntu 18.04 LTS
- All files must be executable
- Code should follow pycodestyle (version 2.5)
- All functions must be type-annotated
- All modules, classes, and functions must have documentation

## Dependencies

The project uses the following Python packages:
- `unittest` (built-in)
- `unittest.mock` (built-in)
- `parameterized`
- `requests`

Install external dependencies:
```bash
pip install parameterized requests
```
