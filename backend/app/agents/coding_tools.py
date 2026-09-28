import json
from typing import Any

from langchain.tools import tool

from app.tools.editor import (
    open_in_vscode as editor_open_in_vscode,
)
from app.tools.filesystem import (
    create_directory as fs_create_directory,
    create_file as fs_create_file,
    edit_file as fs_edit_file,
    list_directory as fs_list_directory,
    read_file as fs_read_file,
    search_files as fs_search_files,
    search_text as fs_search_text,
)
from app.workspace.manager import (
    workspace_manager,
)

from app.tools.terminal import (
    run_tests as terminal_run_tests,
)

from app.tools.git import (
    git_diff as repo_git_diff,
    git_diff_file as repo_git_diff_file,
    git_status as repo_git_status,
)

from app.repository.search import (
    semantic_code_search
    as repository_semantic_search,
)

from app.tools.desktop import (
    open_url as desktop_open_url,
    open_workspace_path
    as desktop_open_workspace_path,
    reveal_in_explorer
    as desktop_reveal_in_explorer,
)

from app.vision.analyzer import (
    analyze_current_screen
    as vision_analyze_current_screen,
)

def _tool_success(
        data:Any,
)->str:
    return json.dumps(
            {"ok":True,
            "data":data,},
            ensure_ascii=False,
            indent=2,
    )

def _tool_error(
     exc: Exception,
)->str:
    return json.dumps(
        {
            "ok": False,
            "error": str(exc),
        },
        ensure_ascii=False,
        indent=2,
    )

@tool
def get_workspace_info()->str:
    """
    Get information about the currently active project workspace.

    Use this when you need to know which project is currently
    selected before performing repository operations.
    """
    try:
        return _tool_success(
            workspace_manager.get_workspace_info()
        )
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)

@tool
def list_directory(
    path:str =".",
)-> str:
    """
    List files and folders inside a directory in the active workspace.

    Use this to explore the repository structure before deciding
    which files should be inspected.

    The path must be relative to the active workspace.
    Use "." for the workspace root.
    """

    try:
        result = fs_list_directory(
            relative_path=path
        )

        return _tool_success(result)
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)


@tool
def read_file(path:str)->str:
    """
    Read the exact contents of a text file in the active workspace.

    Use this before editing an existing file so you are working
    with its current contents.

    The path must be relative to the active workspace.
    """
    try:
        result = fs_read_file(
            relative_path=path
        )

        return _tool_success(result)
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)

@tool
def search_files(query:str,max_results:int = 25,)->str:
    """
    Search the active workspace for files whose filename or path
    contains the query.

    Use this only when searching for a filename or file path.

    Do NOT use this to search for function names, class names,
    identifiers, imports, or code inside files. Use search_text
    for those searches.
    """

    try:
        result = fs_search_files(
                    query=query,
                    max_results=max_results,
        )
        return _tool_success(result)
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)

@tool
def search_text(
    query: str,
    path: str = ".",
    max_results: int = 25,)->str:
    """
    Search inside project files for text.

    Use this to locate functions, classes, identifiers, imports,
    routes, error messages, or other code references.

    The result includes matching file paths and line numbers.
    After locating the relevant source file, use read_file when
    you need its contents before editing or explaining it.

    Use search_files instead when searching for a filename or path.
    """
    try:
        result = fs_search_text(
            query=query,
            relative_path=path,
            max_results=max_results,
        )
        return _tool_success(result)
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)

@tool
def create_directory(
    path: str,
) -> str:
    """
    Create a new directory inside the active workspace.

    Use this only when the requested directory does not already exist.

    The path must be relative to the active workspace.
    """
    try:
        result = fs_create_directory(
            relative_path=path
        )

        return _tool_success(result)

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)


@tool
def create_file(
    path: str,
    content: str,
) -> str:
    """
    Create a new UTF-8 text file inside the active workspace.

    Use this only for a new file. Do not use it to overwrite an
    existing file. Use edit_file for existing files.

    Parent directories must already exist.
    """
    try:
        result = fs_create_file(
            relative_path=path,
            content=content,
        )

        return _tool_success(result)

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)


@tool
def edit_file(
    path: str,
    old_text: str,
    new_text: str,
) -> str:
    """
    Modify one exact section of an existing text file.

    Always read the file first. old_text must exactly match one
    unique section of the current file. Use a larger and more
    specific old_text section if the same text appears multiple times.

    The path must be relative to the active workspace.
    """
    try:
        result = fs_edit_file(
            relative_path=path,
            old_text=old_text,
            new_text=new_text,
        )

        return _tool_success(result)

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)

@tool
def open_in_vscode()->str:
    """
    Open the currently active project workspace in Visual Studio Code.

    Use this when the user explicitly asks to open the project in
    VS Code or when opening the editor is useful for the requested task.
    """
    try:
        result = (
            editor_open_in_vscode()
        )
        return _tool_success(result)
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)

@tool
def run_tests(
    test_path : str = ".",

)-> str:
    """
    Run pytest for the currently active project.

    Use this to verify Python code changes or check whether the
    project's tests currently pass.

    test_path must point to a file or directory inside the active
    workspace. Use "." to run the full test suite.

    Inspect ok, exit_code, stdout, stderr, and timed_out in the
    result before deciding whether the tests passed.
    """

    try:
        result = terminal_run_tests(
            test_path=test_path,
            timeout_seconds=60,
        )
        return json.dumps(
            {
                "ok": result["ok"],
                "data": result,
            },
            ensure_ascii=False,
            indent=2,
        )
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)

@tool
def git_status() -> str:
    """
    Show which files in the active project have Git changes.

    Use this to identify modified, staged, deleted, or untracked
    files without changing the repository.
    """

    try:
        result = repo_git_status()

        return _tool_success(
            result
        )
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)

@tool
def git_diff() -> str:
    """
    Show Git code differences for the active project.

    Use this to inspect tracked code changes across the repository.
    The result contains both unstaged and staged differences.

    Untracked files appear in git_status but normally do not appear
    in git diff until they are tracked by Git.
    """
    try:
        result = repo_git_diff()

        return _tool_success(
            result
        )

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)


@tool
def git_diff_file(
    path: str,
) -> str:
    """
    Show Git differences for one specific file in the active project.

    Use this when you already know which file should be inspected
    and do not need the full repository diff.

    The path must be relative to the active workspace.
    """
    try:
        result = (
            repo_git_diff_file(
                path
            )
        )

        return _tool_success(
            result
        )

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(exc)

@tool
def semantic_code_search(
    query: str,
    limit: int = 5,
) -> str:
    """
    Search the active repository by meaning.

    Use this when you know the concept or behavior you are
    looking for but do not know the exact file, function,
    class, or symbol name.

    Examples:
    - where authentication is handled
    - code responsible for database connection
    - logic that prevents division by zero
    - tests related to user registration

    For exact names, symbols, strings, or error messages,
    prefer search_text instead.
    """

    try:
        results = (
            repository_semantic_search(
                query=query,
                limit=limit,
            )
        )

        return json.dumps(
            {
                "ok": True,
                "data": {
                    "query": query,
                    "count": len(results),
                    "results": [
                        {
                            "path":
                                result.path,

                            "language":
                                result.language,

                            "chunk_type":
                                result.chunk_type,

                            "symbol_name":
                                result.symbol_name,

                            "start_line":
                                result.start_line,

                            "end_line":
                                result.end_line,

                            "similarity":
                                round(
                                    result.similarity,
                                    4,
                                ),

                            "content_preview":
                                result.content[
                                    :2000
                                ],
                        }
                        for result
                        in results
                    ],
                },
            },
            ensure_ascii=False,
            indent=2,
        )

    except (
        ValueError,
        RuntimeError,
    ) as exc:
        return _tool_error(
            exc
        )

@tool
def open_url(
    url: str,
) -> str:
    """
    Open an HTTP or HTTPS URL in the user's default browser.

    Use this when the user explicitly asks to open a web page,
    local development URL, documentation page, or browser-based
    developer interface.

    This is a direct desktop action. Do not use vision when
    opening the URL is sufficient.
    """

    try:
        result = desktop_open_url(
            url
        )

        return json.dumps(
            {
                "ok": True,
                "data": result,
            },
            ensure_ascii=False,
            indent=2,
        )
    except(
        ValueError,
        OSError,
    ) as exc:
        return _tool_error(
            exc
        )

@tool
def open_workspace_path(
    path: str,
) -> str:
    """
    Open an existing file or directory inside the active
    workspace using the operating system's default application.

    Use this only when the user wants the item visibly opened.
    For reading source code or obtaining file contents, use
    read_file instead.
    """

    try:
        result = (
            desktop_open_workspace_path(
                path
            )
        )

        return json.dumps(
            {
                "ok": True,
                "data": result,
            },
            ensure_ascii=False,
            indent=2,
        )

    except (
        ValueError,
        OSError,
    ) as exc:
        return _tool_error(
            exc
        )

@tool
def reveal_in_explorer(
    path: str,
) -> str:
    """
    Reveal an existing workspace file or directory in
    Windows File Explorer.

    Use this when the user explicitly wants to locate or
    reveal a project item visually in Explorer.

    Do not use this merely to inspect source code.
    """

    try:
        result = (
            desktop_reveal_in_explorer(
                path
            )
        )

        return json.dumps(
            {
                "ok": True,
                "data": result,
            },
            ensure_ascii=False,
            indent=2,
        )

    except (
        ValueError,
        OSError,
    ) as exc:
        return _tool_error(
            exc
        )

@tool
def analyze_screen(
    prompt: str,
) -> str:
    """
    Analyze the user's currently visible primary screen using
    the configured vision model.

    Use this only when the required information is visible on
    the screen and cannot be obtained more reliably through
    direct tools such as read_file, search_text, terminal,
    Git, repository search, or other system APIs.

    Appropriate uses include:
    - visible GUI error dialogs
    - browser error pages
    - installer dialogs
    - GUI-only application state
    - visual layout or interface questions

    Do not use this to read source files that read_file can
    access.

    This tool only observes the screen. It does not click,
    type, modify files, or perform desktop actions.
    """

    try:
        result = (
            vision_analyze_current_screen(
                prompt
            )
        )

        return json.dumps(
            {
                "ok": True,
                "data": result,
            },
            ensure_ascii=False,
            indent=2,
        )

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        return _tool_error(
            exc
        )


CODING_TOOLS = [
    get_workspace_info,
    list_directory,
    read_file,
    search_files,
    search_text,
    semantic_code_search,
    create_directory,
    create_file,
    edit_file,
    open_in_vscode,
    run_tests,
    git_status,
    git_diff,
    git_diff_file,
    open_url,
    open_workspace_path,
    reveal_in_explorer,
    analyze_screen,
]
    


    
