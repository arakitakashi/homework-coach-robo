# unit-test

**Delegates unit test execution to a sub-agent and returns only a structured summary.**

## Description

Executes unit tests (Vitest for frontend, pytest for backend) via a sub-agent and returns a concise pass/fail summary. This avoids polluting the main agent's context with verbose test output during TDD cycles.

## When to Use

- **RED phase**: Confirm test fails before implementation
- **GREEN phase**: Confirm test passes after implementation
- **Quick verification**: Check if specific tests pass without verbose logs
- **TDD cycle**: Repeatedly during Test-Driven Development workflow

**Do NOT use for:**
- Full quality checks before PR (use `/quality-check` instead)
- Coverage reports (use `/quality-check` instead)
- Lint or type checks (use `/quality-check` instead)

## Invocation

```
/unit-test <environment> [test-path] [test-name]
```

### Parameters

| Parameter | Required | Description | Examples |
|-----------|----------|-------------|----------|
| `environment` | Yes | Test environment | `frontend`, `backend` |
| `test-path` | No | Path to test file or directory | `components/VoiceInterface.test.tsx`, `tests/unit/services/` |
| `test-name` | No | Specific test name to run | `"should start recording"`, `test_create_session` |

**Note:** If `test-path` is omitted, all tests in the environment are run.

## Output Format

### Success (Pass)

```
✅ Unit Test Result: PASS

Environment: frontend
Path: components/VoiceInterface.test.tsx

Summary:
- Total: 8 tests
- Passed: 8
- Failed: 0
- Duration: 0.5s
```

### Failure (Fail)

```
❌ Unit Test Result: FAIL

Environment: backend
Path: tests/unit/services/test_auth_service.py

Summary:
- Total: 15 tests
- Passed: 13
- Failed: 2
- Duration: 1.2s

Failures:
1. "test_create_session_with_invalid_user"
   AssertionError: Expected 404, got 500

2. "test_delete_session_unauthorized"
   Expected: HTTPException
   Received: None
```

### Error (Command Failed)

```
❌ Unit Test Execution Error

Environment: frontend
Path: components/NonExistent.test.tsx

Error: No test files found matching pattern
Suggestion: Check the test path and ensure the file exists
```

## Examples

### Example 1: RED phase (confirm test fails)

```
User: "VoiceInterfaceのテストを書いた"
Claude: テストが失敗することを確認します

/unit-test frontend components/VoiceInterface.test.tsx

→ ❌ 1/1 tests failed (expected in RED phase)
  - "should start recording": ReferenceError: startRecording is not defined
```

### Example 2: GREEN phase (confirm test passes)

```
Claude: 実装を完了しました。テストを確認します

/unit-test frontend components/VoiceInterface.test.tsx

→ ✅ 1 test passed (0.3s)
```

### Example 3: Multiple tests in a directory

```
Claude: 認証関連のテストをすべて確認します

/unit-test backend tests/unit/services/

→ ✅ 42 tests passed (1.2s)
```

### Example 4: Specific test name

```
Claude: セッション作成のテストのみ実行します

/unit-test backend tests/unit/services/test_session_service.py test_create_session

→ ✅ 1 test passed (0.1s)
```

## Instructions for Sub-Agent

When this skill is invoked, you are a sub-agent responsible for:

1. **Execute the test command**
   - Frontend: `cd frontend && bun test <path> [--test-name]`
   - Backend: `cd backend && uv run pytest <path> [-k <test-name>]`

2. **Parse the output**
   - Extract: total tests, passed, failed, skipped, duration
   - Extract failure details: test name, error message (concise)

3. **Return structured summary only**
   - Use the Output Format specified above
   - Do NOT include verbose test runner output
   - Do NOT include full stack traces
   - Keep the response under 20 lines

4. **Handle errors gracefully**
   - If command fails, explain why
   - Suggest corrections (e.g., "check path", "ensure environment is set up")

### Command Templates

#### Frontend (Vitest)

```bash
# All tests
cd frontend && bun test

# Specific file
cd frontend && bun test <path>

# Specific test name
cd frontend && bun test <path> -t "<test-name>"
```

#### Backend (pytest)

```bash
# All tests
cd backend && uv run pytest tests/

# Specific file
cd backend && uv run pytest <path>

# Specific test name
cd backend && uv run pytest <path> -k "<test-name>"
```

### Parsing Hints

#### Vitest output patterns

```
✓ tests/file.test.tsx (8)        ← File with 8 passing tests
❌ tests/file.test.tsx (1)        ← File with 1 failing test

Test Files  2 passed (2)         ← Summary line
     Tests  13 passed (13)       ← Total tests
  Duration  0.5s                 ← Duration
```

#### pytest output patterns

```
collected 15 items                ← Total tests
==================== 15 passed in 0.50s ====================  ← Summary line
==================== 13 passed, 2 failed in 1.20s ====================  ← Failure case
```

### Error Message Extraction

For failed tests, extract only:
- Test name
- Expected vs Received (if available)
- Error type (AssertionError, TypeError, etc.)
- First line of error message

**Keep each failure under 3 lines.**

## Relationship to Other Skills

| Skill | Purpose | When to Use | Output |
|-------|---------|-------------|--------|
| `/unit-test` | Quick test execution during TDD | RED/GREEN phases | ✅ Pass/Fail summary only |
| `/quality-check` | Full quality verification | Before PR creation | ✅ Lint + Type + Test + Coverage |
| `/analyze-errors` | Error analysis and fix proposals | When errors occur | ✅ Error categorization + fixes |

## Notes

- This skill is optimized for **TDD workflow**
- It prioritizes **speed and context efficiency** over detailed output
- For comprehensive test analysis, use `/quality-check` instead
- The sub-agent keeps verbose logs internally; only the summary is returned
