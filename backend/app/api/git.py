from fastapi import (
    APIRouter,
    HTTPException,
)

from app.tools.git import (
    git_diff,
    git_diff_file,
    git_status,
)

router = APIRouter(
    prefix="/git",
    tags=["Git"],
)


@router.get("/status")
def get_git_status():
    try:
        result = git_status()

        if isinstance(result, dict):
            output = (
                result.get("stdout")
                or result.get("status")
                or ""
            )
        else:
            output = str(
                result or ""
            )

        files = []

        for line in output.splitlines():
            if len(line) < 3:
                continue

            status = line[:2].strip()

            path = line[3:].strip()

            if not path:
                continue

            files.append(
                {
                    "status": status,
                    "path": path,
                }
            )

        return {
            "files": files,
        }

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/diff")
def get_git_diff():
    try:
        result = git_diff()

        if isinstance(
            result,
            dict,
        ):
            diff = (
                result.get("stdout")
                or result.get("diff")
                or ""
            )
        else:
            diff = str(
                result or ""
            )

        return {
            "diff": diff,
        }

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.get("/diff-file")
def get_git_file_diff(
    path: str,
):
    try:
        return git_diff_file(
            path
        )

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc