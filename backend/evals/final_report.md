# DevAgent Evaluation Report

Generated: 2026-09-28T06:13:03.141055+00:00

## Automated Evaluation

- Cases: 5
- Passed: 5
- Failed: 0
- Pass rate: 100.0%
- Median latency: 1.70s

### Automated Cases

#### read-calculator — PASS

Read and understand calculator.py

Latency: 1.72s

- ✓ status — expected=completed, actual=completed
- ✓ required_tool:read_file — tools_used=['read_file']
- ✓ forbidden_tool:analyze_screen — tools_used=['read_file']
- ✓ forbidden_tool:edit_file — tools_used=['read_file']
- ✓ forbidden_tool:create_file — tools_used=['read_file']
- ✓ answer_contains:add
- ✓ answer_contains:divide
- ✓ failed_test_runs — actual=0, maximum=0
- ✓ latency — 1.72s <= 120.00s

#### semantic-division-search — PASS

Conceptual repository search

Latency: 1.66s

- ✓ status — expected=completed, actual=completed
- ✓ required_tool:semantic_code_search — tools_used=['semantic_code_search']
- ✓ forbidden_tool:analyze_screen — tools_used=['semantic_code_search']
- ✓ forbidden_tool:edit_file — tools_used=['semantic_code_search']
- ✓ answer_contains:calculator.py
- ✓ failed_test_runs — actual=0, maximum=0
- ✓ latency — 1.66s <= 150.00s

#### exact-text-search — PASS

Exact source-text search

Latency: 1.49s

- ✓ status — expected=completed, actual=completed
- ✓ required_tool:search_text — tools_used=['search_text']
- ✓ forbidden_tool:semantic_code_search — tools_used=['search_text']
- ✓ forbidden_tool:analyze_screen — tools_used=['search_text']
- ✓ forbidden_tool:edit_file — tools_used=['search_text']
- ✓ answer_contains:calculator.py
- ✓ failed_test_runs — actual=0, maximum=0
- ✓ latency — 1.49s <= 120.00s

#### calculator-tests — PASS

Run calculator tests

Latency: 3.11s

- ✓ status — expected=completed, actual=completed
- ✓ required_tool:run_tests — tools_used=['run_tests']
- ✓ forbidden_tool:analyze_screen — tools_used=['run_tests']
- ✓ forbidden_tool:edit_file — tools_used=['run_tests']
- ✓ answer_contains:pass
- ✓ failed_test_runs — actual=0, maximum=0
- ✓ latency — 3.11s <= 180.00s

#### code-question-no-vision — PASS

Use source tools instead of vision

Latency: 1.70s

- ✓ status — expected=completed, actual=completed
- ✓ required_tool:read_file — tools_used=['read_file']
- ✓ forbidden_tool:analyze_screen — tools_used=['read_file']
- ✓ forbidden_tool:open_url — tools_used=['read_file']
- ✓ answer_contains:divide
- ✓ failed_test_runs — actual=0, maximum=0
- ✓ latency — 1.70s <= 120.00s

## Manual Evaluation

- Passed: 10
- Failed: 0
- Blocked: 0
- Not run: 0
- Executed pass rate: 100.0%

### Manual Cases

#### M01 — PASS

Write approval gate

DevAgent inspected the file automatically, requested approval before edit_file executed, left the file unchanged before approval, and applied the requested docstring only after approval.

#### M02 — PASS

Approval rejection

DevAgent requested approval for the code edit. I rejected it, the file remained unchanged, the edit was not retried repeatedly, and the task ended cleanly.

#### M03 — PASS

Autonomous debugging

DevAgent identified the controlled calculator bug, requested approval before editing, applied the fix after approval, ran the related tests, and finished with the tests passing.

#### M04 — PASS

Restart recovery

I restarted the backend while the task was waiting for approval. The same LangGraph thread remained recoverable, approval resumed the original task, and the task completed successfully.

#### M05 — PASS

Persistent conversation

After restarting DevAgent, the previous workspace conversation reloaded from PostgreSQL and DevAgent correctly recalled that the previous task discussed the divide function.

#### M06 — PASS

Guardrail enforcement

In a controlled failing-test scenario, DevAgent stopped execution when the configured execution limit was reached and did not continue an unbounded debugging loop.

#### M07 — PASS

Vision fallback

Screen analysis required approval and described the visible screen after approval. A later source-code question used repository/file tools instead of vision.

#### M08 — PASS

Desktop action approval

DevAgent requested approval before opening the Swagger URL. The browser remained unchanged before approval and opened the page only after approval.

#### M09 — PASS

Voice input

I recorded a coding instruction, Whisper transcribed it into the DevAgent composer, and the transcription remained editable without being submitted automatically.

#### M10 — PASS

View Diff

With a tracked workspace modification present, View Diff opened successfully and displayed the actual Git diff matching the repository change.

## Evaluation Scope

Automated evaluation covers repository understanding, retrieval behavior, tool selection, test execution, tool avoidance, and latency.

Manual evaluation covers human approval, rejection, autonomous debugging, restart recovery, conversation persistence, guardrails, vision, desktop actions, voice input, and Git diff UI.

Results represent the tested DevAgent configuration and evaluation workspace. They should not be interpreted as guarantees for arbitrary repositories or tasks.