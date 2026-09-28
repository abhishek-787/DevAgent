from dataclasses import (
    dataclass,
)
from enum import (
    Enum,
)


class PermissionCategory(
    str,
    Enum,
):
    SAFE_READ = "safe_read"

    CONTROLLED_EXECUTION = (
        "controlled_execution"
    )

    WORKSPACE_WRITE = (
        "workspace_write"
    )

    DESKTOP_ACTION = (
        "desktop_action"
    )

    SENSITIVE_OBSERVATION = (
        "sensitive_observation"
    )

@dataclass(
    frozen=True
)
class ToolPermission:
    category: PermissionCategory

    mutates_workspace: bool = False

    executes_code: bool = False

    external_action: bool = False

    accesses_sensitive_data: bool = False

    description: str = ""

TOOL_PERMISSIONS: dict[
    str,
    ToolPermission,
] = {
        "get_workspace_info":
        ToolPermission(
            category=(
                PermissionCategory
                .SAFE_READ
            ),
            description=(
                "Read active workspace "
                "information."
            ),
        ),

    "list_directory":
        ToolPermission(
            category=(
                PermissionCategory
                .SAFE_READ
            ),
            description=(
                "List files and folders "
                "inside the workspace."
            ),
        ),

    "read_file":
        ToolPermission(
            category=(
                PermissionCategory
                .SAFE_READ
            ),
            description=(
                "Read an existing "
                "workspace file."
            ),
        ),

    "search_files":
        ToolPermission(
            category=(
                PermissionCategory
                .SAFE_READ
            ),
        ),

    "search_text":
        ToolPermission(
            category=(
                PermissionCategory
                .SAFE_READ
            ),
        ),

    "semantic_code_search":
        ToolPermission(
            category=(
                PermissionCategory
                .SAFE_READ
            ),
        ),
    "git_status":
        ToolPermission(
            category=(
                PermissionCategory
                .SAFE_READ
            ),
        ),

    "git_diff":
        ToolPermission(
            category=(
                PermissionCategory
                .SAFE_READ
            ),
        ),

    "git_diff_file":
        ToolPermission(
            category=(
                PermissionCategory
                .SAFE_READ
            ),
        ),
    "run_tests":
        ToolPermission(
            category=(
                PermissionCategory
                .CONTROLLED_EXECUTION
            ),
            executes_code=True,
            description=(
                "Run the project test "
                "suite through the "
                "controlled terminal."
            ),
        ),
    "create_directory":
        ToolPermission(
            category=(
                PermissionCategory
                .WORKSPACE_WRITE
            ),
            mutates_workspace=True,
            description=(
                "Create a directory "
                "inside the workspace."
            ),
        ),

    "create_file":
        ToolPermission(
            category=(
                PermissionCategory
                .WORKSPACE_WRITE
            ),
            mutates_workspace=True,
            description=(
                "Create a new file "
                "inside the workspace."
            ),
        ),

    "edit_file":
        ToolPermission(
            category=(
                PermissionCategory
                .WORKSPACE_WRITE
            ),
            mutates_workspace=True,
            description=(
                "Modify an existing "
                "workspace file."
            ),
        ),
    "open_in_vscode":
        ToolPermission(
            category=(
                PermissionCategory
                .DESKTOP_ACTION
            ),
            external_action=True,
            description=(
                "Open the active project "
                "in VS Code."
            ),
        ),

    "open_url":
        ToolPermission(
            category=(
                PermissionCategory
                .DESKTOP_ACTION
            ),
            external_action=True,
            description=(
                "Open a web URL in the "
                "default browser."
            ),
        ),

    "open_workspace_path":
        ToolPermission(
            category=(
                PermissionCategory
                .DESKTOP_ACTION
            ),
            external_action=True,
        ),

    "reveal_in_explorer":
        ToolPermission(
            category=(
                PermissionCategory
                .DESKTOP_ACTION
            ),
            external_action=True,
        ),
    "analyze_screen":
        ToolPermission(
            category=(
                PermissionCategory
                .SENSITIVE_OBSERVATION
            ),
            accesses_sensitive_data=True,
            description=(
                "Capture and analyze the "
                "user's visible screen."
            ),
        ),

}

APPROVAL_REQUIRED_CATEGORIES = {
    PermissionCategory.WORKSPACE_WRITE,
    PermissionCategory.DESKTOP_ACTION,
    PermissionCategory.SENSITIVE_OBSERVATION,
}


def get_tool_permission(
    tool_name: str,
) -> ToolPermission:
    permission = (
        TOOL_PERMISSIONS.get(
            tool_name
        )
    )

    if permission is None:
        raise ValueError(
            "Tool is not registered "
            f"in permission system: "
            f"{tool_name}"
        )

    return permission

def validate_tool_registry(
    tool_names: set[str],
) -> None:

    registered_names = set(
        TOOL_PERMISSIONS.keys()
    )

    missing = (
        tool_names
        - registered_names
    )

    if missing:
        missing_text = ", ".join(
            sorted(
                missing
            )
        )

        raise RuntimeError(
            "Tools missing permission "
            "definitions: "
            f"{missing_text}"
        )

def requires_human_aproval(
        tool_name:str,
)->bool:
    permission = get_tool_permission(
        tool_name
    )

    return (
        permission.category
        in APPROVAL_REQUIRED_CATEGORIES
    )