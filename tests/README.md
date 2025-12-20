# Tests

This directory contains global or general tests for the project. **Module-specific tests should be placed in their respective directories (e.g., `server/tests/`, `sdk/tests/`).**

## How to Run Tests

This project uses `pytest` as the testing framework.

### 1. Install Dependencies

Ensure you have installed the development dependencies (including `pytest`). Run the following command from the project root:

```bash
# Install the server module and its dev dependencies
pip install -e server[dev]
```

### 2. Run Tests

Run the following command from the project root:

```bash
pytest
```

### 3. Test File Explanations

#### `test_dummy.py`

- **Purpose**: A placeholder test file used to verify if the test environment is configured correctly (e.g., verifying `1+1=2`).
- **Style**: It uses the Python standard library `unittest` style (based on `unittest.TestCase`).
- **Recommendation**: Although `pytest` is compatible with this style, we **recommend using the native Pytest style** (writing functions + `assert` directly) for this project as it is more concise and powerful. Please refer to the code in `server/tests/` for examples.

#### `pyproject.toml` (located in `server/`)

Although this file is not in the `tests/` directory, it is crucial for testing:

- **Dependency Management**: Defines project dependencies (`dependencies`) and development dependencies (`dev`, including `pytest`).
- **Build System**: Ensures the `server` directory is installed as a Python package, allowing test code to import source code via `import` statements.

### 4. Directory Structure

- `tests/`: Global or general tests.
- `server/tests/`: Dedicated tests for the backend server module.
- `sdk/tests/`: Dedicated tests for the SDK module.
