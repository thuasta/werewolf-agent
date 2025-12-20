# Testing Guide & Change Log

This document records the setup process of the testing framework and provides a guide for team members on writing test cases, automated test scripts, and maintaining the test platform.

## 1. Work Done

To support long-term maintenance and collaboration, we have adjusted and set up the testing architecture as follows:

### 1.1 Modular Testing Structure

- **Action**: Created a `tests/` folder under the `server/` directory.
- **Result**: Backend module test code is now located in `server/tests/` instead of being piled up in the root `tests/` directory.
- **Purpose**: To implement **modular testing**. Co-locating test code with the source code helps developers quickly find relevant tests and run tests for specific modules independently.

### 1.2 Automated Testing Framework (Pytest)

- **Action**: Created/Updated `pytest.ini` configuration file.
- **Configuration**:
  ```ini
  [pytest]
  pythonpath = server sdk      # Allows test code to import modules from server and sdk directly
  testpaths = tests server/tests sdk/tests # Tells pytest where to look for test files
  python_files = test_*.py     # Identifies files starting with test_ as test files
  ```
- **Purpose**: `pytest` is the most popular testing framework in the Python community, being more concise and powerful than the built-in `unittest`.

### 1.3 Basic Test Cases

- **Action**: Wrote preliminary test files based on `Game`, `Player`, and `GameConfig` class definitions:
  - `server/tests/test_game.py`
  - `server/tests/test_player.py`
  - `server/tests/test_game_config.py`
- **Purpose**: To provide "Red Light" (test failure) standards for backend development. Once the corresponding features are implemented, these tests should turn "Green" (pass). This is the foundation of **Test-Driven Development (TDD)**.

### 1.4 CI/CD Workflow (GitHub Actions)

- **Action**: Modified `.github/workflows/build.yml`.
- **Changes**:
  - Changed the test runner command to `pytest`.
  - Added `pip install -e server[dev]` step to ensure server code is installed in editable mode, resolving import path issues.
  - Configured code coverage reporting (`--cov`).
- **Purpose**: **Automated Testing**. Every time code is pushed to `dev` or `main` branches, GitHub automatically runs all tests. If tests fail, the code cannot be merged, ensuring the stability of the main branch.

---

2.  **Run**: Type `pytest` in the terminal.

### 2.1 What are Automated Test Scripts?

In our project, **Automated Test Scripts** refer to these `test_*.py` files.
They are "automated" because we don't need to manually click buttons or enter commands to test features. `pytest` automatically collects all files, runs all functions, and reports results.

Combined with GitHub Actions, this automation is pushed to the limit: **Tests run automatically whenever you push code.**

### 2.2 How to Run Modular Tests?

Since we use a modular structure, you can run tests for specific parts without waiting for all tests to finish:

- **Run all tests**:
  ```powershell
  pytest
  ```
- **Run tests for the server module only**:
  ```powershell
  pytest server/tests
  ```
- **Run tests for a specific file**:
  ```powershell
  pytest server/tests/test_game.py
  ```

## 3. Extending Tests (For Other Groups)

As the project grows, we need to test the SDK, new backend features, and other tasks. Here are the specific steps:

### 3.1 Testing the SDK

The basic structure for SDK testing has been set up.

1.  **Location**: Place all SDK-related test code in the `sdk/tests/` directory.
2.  **Writing**:
    - Create a new file `sdk/tests/test_client.py` (example).
    - Write test cases, such as testing connection, message sending, etc.
3.  **Running**:
    - Run all SDK tests: `pytest sdk/tests`

### 3.2 Testing New Backend Code

When backend developers add new files (e.g., `voting.py`) in `server/game_logic` or `server/agent_server`:

1.  **Create Corresponding Test File**: Create `test_voting.py` in `server/tests/`.
2.  **Follow TDD Process**:
    - Write test first: Write `test_vote_success()` based on requirements.
    - Run test: It will fail (because the feature isn't written yet).
    - Implement feature: Implement code in `server/game_logic/voting.py`.
    - Run again: Test passes.

### 3.3 Testing New Tasks/Modules

If a completely new module (e.g., `ai_analysis`) is added to the project:

1.  **Create Directory**: Create a `tests/` folder in the module's root directory.
2.  **Configure Path**: Modify `pytest.ini`:
    - Append the new module path to `pythonpath` (space-separated).
    - Append the new test directory to `testpaths` (space-separated).
3.  **Write & Run**: Follow the standard process above to write and run tests.

## 4. Next Steps

For the testing team and developers:

1.  **Monitor Backend Progress**: When backend developers implement `Game.start()`, modify `test_game.py` to remove `pytest.raises(NotImplementedError)` and assert that `game._state` becomes `EVENING`.
2.  **Add Boundary Conditions**: Current tests are "Happy Paths" (normal cases). Write "Exception Paths" tests, such as:
    - What if player count and character count in config don't match?
    - What if illegal arguments are passed?
3.  **Maintain CI/CD**: If GitHub Actions fail, check the logs to analyze if it's a code bug or a test case error.
