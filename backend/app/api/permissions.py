from fastapi import (
    APIRouter,
)

from app.security.permissions import (
    TOOL_PERMISSIONS,
)


router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)

@router.get("/tools")
def get_tool_permissions():

    return {
        "count":
            len(
                TOOL_PERMISSIONS
            ),

        "tools": {
            tool_name: {
                "category":
                    permission
                    .category
                    .value,

                "mutates_workspace":
                    permission
                    .mutates_workspace,

                "executes_code":
                    permission
                    .executes_code,

                "external_action":
                    permission
                    .external_action,

                "accesses_sensitive_data":
                    permission
                    .accesses_sensitive_data,

                "description":
                    permission
                    .description,
            }

            for (
                tool_name,
                permission,
            )
            in TOOL_PERMISSIONS.items()
        },
    }