from evals.models import (
    EvalCase,
)


AUTOMATED_CASES: tuple[
    EvalCase,
    ...
] = (

    EvalCase(
        id="read-calculator",
        category="file_understanding",
        title=(
            "Read and understand "
            "calculator.py"
        ),
        prompt=(
            "Read "
            "app/services/calculator.py "
            "and briefly tell me what "
            "functions it contains."
        ),
        required_tools=(
            "read_file",
        ),
        forbidden_tools=(
            "analyze_screen",
            "edit_file",
            "create_file",
        ),
        answer_contains=(
            "add",
            "divide",
        ),
        max_latency_seconds=120,
    ),


    EvalCase(
        id="semantic-division-search",
        category="repository_rag",
        title=(
            "Conceptual repository "
            "search"
        ),
        prompt=(
            "Find the code responsible "
            "for preventing division by "
            "zero. Assume I do not know "
            "the exact function or symbol "
            "name. Briefly tell me where "
            "it is handled."
        ),
        required_tools=(
            "semantic_code_search",
        ),
        forbidden_tools=(
            "analyze_screen",
            "edit_file",
        ),
        answer_contains=(
            "calculator.py",
        ),
        max_latency_seconds=150,
    ),


    EvalCase(
        id="exact-text-search",
        category="tool_selection",
        title=(
            "Exact source-text search"
        ),
        prompt=(
            "Find the exact text "
            "\"def divide\" "
            "in the current repository "
            "and tell me which file "
            "contains it."
        ),
        required_tools=(
            "search_text",
        ),
        forbidden_tools=(
            "semantic_code_search",
            "analyze_screen",
            "edit_file",
        ),
        answer_contains=(
            "calculator.py",
        ),
        max_latency_seconds=120,
    ),


    EvalCase(
        id="calculator-tests",
        category="test_execution",
        title=(
            "Run calculator tests"
        ),
        prompt=(
            "Run the calculator tests "
            "in tests/test_calculator.py "
            "and briefly report the "
            "result."
        ),
        required_tools=(
            "run_tests",
        ),
        forbidden_tools=(
            "analyze_screen",
            "edit_file",
        ),
        answer_contains=(
            "pass",
        ),
        max_failed_test_runs=0,
        max_latency_seconds=180,
    ),


    EvalCase(
    id="code-question-no-vision",
    category="tool_selection",
    title=(
        "Use source tools instead "
        "of vision"
    ),
    prompt=(
        "Read "
        "app/services/calculator.py "
        "from the current workspace now "
        "and briefly explain what the "
        "divide function does."
    ),
    required_tools=(
        "read_file",
    ),
    forbidden_tools=(
        "analyze_screen",
        "open_url",
    ),
    answer_contains=(
        "divide",
    ),
    max_latency_seconds=120,
),
)