import json
import uuid
import re

from langchain_core.messages import (
    AIMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import (
    START,
    END,
    MessagesState,
    StateGraph,
)

from langgraph.types import (
    Command,
    interrupt,
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)

from app.agents.coding_tools import (
    CODING_TOOLS,
)
from app.agents.model import (
    coding_model,
)

from app.security.permissions import (
    validate_tool_registry,
)


from app.security.permissions import (
    get_tool_permission,
    requires_human_aproval,
)

from app.security.guardrails import (
    check_execution_limits,
    limit_conversation_context,
    limit_memory_context,
)

from app.agents.checkpointing import (
    checkpointer,
)


class CodingAgentState(
    MessagesState
):
    tool_rounds: int
    failed_test_runs:int
    tests_status: str
    memory_context: str
    conversation_context: str


CODING_AGENT_PROMPT = """
You are DevAgent, a local AI coding agent.

You work on the user's currently selected project through
controlled tools.

Your goal is to complete the user's requested coding task
using the smallest useful sequence of actions.

GENERAL RULES

1. For requests that depend on the local project, use tools.
   Never invent file contents, paths, or tool results.

2. For general programming questions that do not depend on
   the workspace, answer directly without tools.

3. Perform only actions required for the user's request.

4. Do not open VS Code unless the user explicitly asks you
   to open the project in VS Code.

5. Do not repeat a tool after it has already succeeded unless
   another call is genuinely necessary.

6. Stop using tools when the requested task is complete.

PROJECT INSPECTION

7. If the user provides an exact file path, use that path
   directly. Do not search or list the repository first unless
   the path fails.

8. When looking for files or modules by name, prefer
   search_files.

9. Use search_text when looking for functions, classes,
   identifiers, imports, routes, error messages, or other text
   inside project files.

10. If you still do not know where relevant code is located,
    use list_directory when useful.

11. Read an existing file before making claims about its
    contents.

When a workspace file is needed, never ask the user to provide
its contents. You have read_file for that purpose.

After search_text or search_files identifies a relevant file,
call read_file on the relevant path when its contents are needed.

During an authorized coding or debugging task, continue using
available tools until the requested task is complete. Do not stop
to ask the user for information that can be obtained from the
workspace tools.

For a symbol such as a function or class, prefer searching for a
specific definition such as "def multiply" rather than a broad
word when useful.

EDITING

12. Always read an existing file before editing it.

13. Use edit_file only with exact text taken from the current
    file contents.

14. Modify only files required for the user's task.

15. Use create_file only when creating a new file.

16. If a required parent directory does not exist, create the
    directory before creating the file.

VERIFICATION

17. If a tool returns ok=false, do not claim success.
    Inspect the error and choose an appropriate recovery action.

18. Only report that something was created, edited, found,
    or opened after a tool confirms success.

19. After a successful modification, verify the result when
    verification is useful and does not require unnecessary
    actions.

COMPLETION

20. When the requested task is complete, stop using tools and
    give a concise final response.

21. Do not perform optional actions merely to demonstrate
    capabilities.

22. Do not output tool-call JSON as the final response.

23. Do not narrate private reasoning, internal deliberation,
    self-talk, or alternative possibilities.

24. Final responses should normally be concise unless the
    user explicitly asks for a detailed explanation.

TESTING

25. Use run_tests when the user's request requires verification
    of Python code or when verifying a code modification is useful.

26. Prefer run_tests instead of attempting to describe how the
    user could run pytest manually.

27. A test run succeeds only when the tool reports ok=true and
    exit_code=0.

28. If run_tests reports ok=false, do not claim that the tests
    passed.

29. Never invent test results.

GIT INSPECTION

Use git_status when you need to know which project files have
changed.

Use git_diff when you need to inspect the actual tracked code
changes across the repository.

Use git_diff_file when the relevant changed file is already known
and only that file's diff is needed.

Git inspection tools are read-only. Do not claim that files were
staged, committed, restored, or pushed.

Remember that completely untracked files may appear in git_status
without appearing in git_diff.

After modifying code, inspect Git changes when doing so is useful
for verifying what was actually changed.

AUTONOMOUS DEBUGGING

When the user asks you to fix, debug, repair, or verify broken
Python code:

1. Run the relevant tests when the current failure is not already
   known from reliable tool output.

2. If tests fail, inspect the actual pytest output before making
   changes. Do not guess the failure.

3. When a tool is required for the next action, CALL THE TOOL
   immediately. Do not describe the tool you intend to call.

4. Never write tool-call JSON, example tool calls, or future tool
   instructions in normal assistant text.

5. Do not return a final answer while the requested debugging task
   is still incomplete and another available tool is required.

6. If the failure output already identifies a relevant file path,
   use that path directly rather than searching unnecessarily.

7. Use search_files only when searching for filenames or paths.
   Use search_text when searching for functions, classes,
   identifiers, imports, error messages, or code inside files.

8. Read the relevant source file before editing it.

9. Make the smallest reasonable source-code change that addresses
   the observed failure. Do not modify tests unless the user
   explicitly asks you to modify tests.

10. After every code change made for a debugging task, run the
    relevant tests again before reporting success.

11. If tests still fail, inspect the NEW failure output before
    attempting another fix. Do not repeat the same unsuccessful
    edit.

12. When tests pass, inspect Git changes when requested or useful,
    then give a concise verified summary.

13. Never claim that tests pass unless run_tests reports ok=true
    and exit_code=0.

14. If the user only asks you to inspect or run tests, do not
    modify files unless they explicitly asked you to fix or
    change code.

REPOSITORY SEARCH

You have two different code search methods.

Use search_text when you know an exact symbol, function name,
class name, error message, string, or code fragment.

Use semantic_code_search when you know the behavior or concept
you are looking for but do not know its exact name or location.

Semantic search is for discovering relevant code locations.
Before modifying existing code, inspect the relevant file with
read_file so that edits are based on the current source.

DESKTOP AND VISION

Prefer direct system tools over visual interpretation.

Use filesystem, repository search, terminal, Git, and other
direct tools whenever they can provide the required information.

Use open_url, open_workspace_path, or reveal_in_explorer only
when the user wants a visible desktop action.

Use analyze_screen only when the required information exists
visually on the current screen and cannot be obtained more
reliably through a direct tool.

Do not use vision merely to read project source code, terminal
output that can be obtained directly, Git state, or repository
content.

Vision is observation only. Never claim that analyze_screen
clicked, typed, changed, or interacted with the interface.

After performing a direct desktop action, do not automatically
use vision unless the task also requires visual information.

VISIBLE RESPONSE STYLE

Your final response is shown directly in the DevAgent desktop
conversation panel.

Keep final responses concise, clean, and task-focused.

Do not dump file contents, source code, tool output, JSON, Git output,
or test output into the final response unless the user explicitly asks
to see those details.

For file-reading tasks:
- Confirm that the file was read.
- Briefly summarize what was found.
- Mention important functions, classes, or behavior when useful.
- Do not reproduce the entire file.

For search tasks:
- Briefly state what was found and where.

For test tasks:
- State whether the tests passed or failed.
- Give a short result such as "4 tests passed."
- Do not paste full pytest output unless requested.

For code-editing tasks:
- Briefly state what changed.
- Mention the affected file.
- Mention test status when tests were run.
- Do not reproduce the entire modified file unless requested.

For Git inspection:
- Summarize the relevant changes.
- Do not paste the full diff unless requested.

If the user explicitly asks:
- "show me the code"
- "show the file"
- "show the diff"
- "show the test output"
then provide the requested details.

Prefer short responses such as:

"Completed reading `app/services/calculator.py`. It contains five
calculator functions: add, subtract, multiply, square, and divide."

"Updated `app/services/calculator.py` with the requested change.
The related tests pass."

"Ran the calculator tests successfully: 4 tests passed."

Avoid unnecessary phrases, long explanations, and raw implementation
details unless they help answer the user's actual request.
"""

agent_model = coding_model.bind_tools(
    CODING_TOOLS
)

TOOL_NAMES = {
    coding_tool.name
    for coding_tool in CODING_TOOLS
}

validate_tool_registry(
    TOOL_NAMES
)


def _normalize_tool_call_response(
    response: AIMessage,
) -> AIMessage:
    """
    Preserve native tool calls.

    As a compatibility fallback, accept exactly one valid
    tool-call JSON object returned as:

    1. Raw JSON
    2. A JSON Markdown block
    3. Prose followed by one JSON Markdown block

    Multiple tool-call blocks are not executed.
    """

    if response.tool_calls:
        return response

    if not isinstance(
        response.content,
        str,
    ):
        return response

    content = response.content.strip()

    if not content:
        return response

    candidates = []

    if (
        content.startswith("{")
        and content.endswith("}")
    ):
        candidates.append(content)

    fenced_blocks = re.findall(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        content,
        flags=(
            re.IGNORECASE
            | re.DOTALL
        ),
    )

    candidates.extend(
        fenced_blocks
    )

    valid_tool_calls = []

    for candidate in candidates:
        try:
            parsed = json.loads(
                candidate
            )
        except json.JSONDecodeError:
            continue

        if not isinstance(
            parsed,
            dict,
        ):
            continue

        tool_name = parsed.get(
            "name"
        )

        if "arguments" in parsed:
            arguments = parsed[
                "arguments"
            ]

        elif "args" in parsed:
            arguments = parsed[
                "args"
            ]

        else:
            arguments = {}

        if (
            isinstance(
                tool_name,
                str,
            )
            and tool_name
            in TOOL_NAMES
            and isinstance(
                arguments,
                dict,
            )
        ):
            valid_tool_calls.append(
                {
                    "name": tool_name,
                    "args": arguments,
                }
            )

    if len(valid_tool_calls) != 1:
        return response

    tool_call = (
        valid_tool_calls[0]
    )

    return AIMessage(
        content="",
        tool_calls=[
            {
                "name":
                    tool_call["name"],
                "args":
                    tool_call["args"],
                "id":
                    "call_"
                    + uuid.uuid4().hex,
                "type":
                    "tool_call",
            }
        ],
    )

def coding_agent_node(
    state: CodingAgentState,
):
    tool_rounds = state.get(
        "tool_rounds",
        0,
    )

    failed_test_runs = state.get(
        "failed_test_runs",
        0,
    )

    guardrail = (
        check_execution_limits(
            tool_rounds=tool_rounds,
            failed_test_runs=(
                failed_test_runs
            ),
        )
    )

    if not guardrail.allowed:
        return {
            "messages": [
                AIMessage(
                    content=(
                        "The task was stopped "
                        "by an execution "
                        "guardrail. "
                        f"{guardrail.reason}"
                    )
                )
            ]
        }

    system_prompt = (
        CODING_AGENT_PROMPT
    )

    conversation_context = (
        limit_conversation_context(
            state.get(
                "conversation_context",
                "",
            )
        )
    )

    if conversation_context:
        system_prompt += (
            "\n\n"
        "RECENT WORKSPACE "
        "CONVERSATION HISTORY\n\n"

        "The following is recent "
        "conversation history for "
        "the current workspace.\n"

        "Use it only as contextual "
        "memory when the user's "
        "current request depends on "
        "previous tasks or discussion.\n"

        "Do not invent details that "
        "are not present in this "
        "history.\n"

        "Current instructions and "
        "security policies still "
        "take priority.\n\n"
            + conversation_context
        )

    response = agent_model.invoke(
        [
            SystemMessage(
                content=system_prompt
            ),
            *state["messages"],
        ]
    )

    response = (
        _normalize_tool_call_response(
            response
        )
    )

    return {
        "messages": [
            response
        ]
    }

def update_execution_state(
    state: CodingAgentState,
):
    tool_rounds = (
        state.get(
            "tool_rounds",
            0,
        )
        + 1
    )

    failed_test_runs = state.get(
        "failed_test_runs",
        0,
    )

    tests_status = state.get(
        "tests_status",
        "not_run",
    )

    for message in reversed(
        state["messages"]
    ):
        if not isinstance(
            message,
            ToolMessage,
        ):
            break

        if message.name != "run_tests":
            continue

        try:
            tool_result = json.loads(
                message.content
            )
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            continue

        if not isinstance(
            tool_result,
            dict,
        ):
            continue

        if tool_result.get("ok") is True:
            tests_status = "passed"

        elif tool_result.get("ok") is False:
            tests_status = "failed"
            failed_test_runs += 1

    return {
        "tool_rounds": tool_rounds,
        "failed_test_runs":
            failed_test_runs,
        "tests_status":
            tests_status,
    }

def route_after_agent(
    state: CodingAgentState,
) -> str:

    last_message = (
        state["messages"][-1]
    )

    if not isinstance(
        last_message,
        AIMessage,
    ):
        return "end"

    if not last_message.tool_calls:
        return "end"

    for tool_call in (
        last_message.tool_calls
    ):
        tool_name = (
            tool_call["name"]
        )

        if requires_human_aproval(
            tool_name
        ):
            return "approval"

    return "tools"

def approval_node(
    state: CodingAgentState,
) -> Command:

    last_message = (
        state["messages"][-1]
    )

    if not isinstance(
        last_message,
        AIMessage,
    ):
        raise RuntimeError(
            "Approval node expected "
            "an AIMessage."
        )

    if not last_message.tool_calls:
        raise RuntimeError(
            "Approval node expected "
            "tool calls."
        )

    tool_requests = []

    for tool_call in (
        last_message.tool_calls
    ):
        tool_name = (
            tool_call["name"]
        )

        permission = (
            get_tool_permission(
                tool_name
            )
        )

        tool_requests.append(
            {
                "tool_name":
                    tool_name,

                "arguments":
                    tool_call[
                        "args"
                    ],

                "category":
                    permission
                    .category
                    .value,

                "requires_approval":
                    requires_human_aproval(
                        tool_name
                    ),

                "description":
                    permission
                    .description,
            }
        )

    decision = interrupt(
        {
            "type":
                "tool_approval",

            "message":
                "DevAgent wants to "
                "perform an action "
                "that requires approval.",

            "tools":
                tool_requests,
        }
    )

    approved = bool(
        decision.get(
            "approved",
            False,
        )
    )

    if approved:
        return Command(
            goto="tools"
        )

    rejected_messages = []

    for tool_call in (
        last_message.tool_calls
    ):
        rejected_messages.append(
            ToolMessage(
                content=(
                    '{"ok": false, '
                    '"error": '
                    '"User rejected '
                    'this action."}'
                ),
                name=(
                    tool_call["name"]
                ),
                tool_call_id=(
                    tool_call["id"]
                ),
            )
        )

    return Command(
        goto="rejection_finalizer",
        update={
            "messages":
                rejected_messages
        },
    )

def rejection_finalizer(
    state: CodingAgentState,
):
    return {
        "messages": [
            AIMessage(
                content=(
                    "The requested action "
                    "was not performed "
                    "because you rejected "
                    "the approval request."
                )
            )
        ]
    }


tool_node = ToolNode(CODING_TOOLS)

builder = StateGraph(
    CodingAgentState
)

builder.add_node(
    "agent",
    coding_agent_node,
)

builder.add_node(
    "tools",
    tool_node,
)

builder.add_node(
    "update_execution_state",
    update_execution_state,
)

builder.add_node(
    "approval",
    approval_node,
)

builder.add_node(
    "rejection_finalizer",
    rejection_finalizer,
)

builder.add_edge(
    START,
    "agent",
)

builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools":"tools",
        "approval":"approval",
        "end":END,
    }
)

builder.add_edge(
    "tools",
    "update_execution_state",
)

builder.add_edge(
    "update_execution_state",
    "agent",
)

builder.add_edge(
    "rejection_finalizer",
    END,
)



coding_agent_graph = (
    builder.compile(
        checkpointer=checkpointer
    )
)