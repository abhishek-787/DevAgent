import httpx
from fastapi import FastAPI

from app.core.config import settings

from app.api.workspace import router as workspace_router

app = FastAPI(
    title=settings.app_name,
)

from app.api.files import (
    router as files_router,
)

from app.api.agent import (
    router as agent_router,
)

from app.api.terminal import (
    router as terminal_router,
)

from app.api.git import (
    router as git_router,
)

from app.api.repository import (
    router as repository_router,
)

from app.api.desktop import (
    router as desktop_router,
)

from app.api.vision import (
    router as vision_router,
)

from app.api.voice import (
    router as voice_router,
)

from app.api.permissions import (
    router as permissions_router,
)

from app.api.memory import (
    router as memory_router,
)

from app.api.guardrails import (
    router as guardrails_router,
)

from app.api.audit import (
    router as audit_router,
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
    }


@app.get("/system/status")
async def system_status():
    required_models = {
        "coding": settings.coding_model,
        "general": settings.general_model,
        "vision": settings.vision_model,
        "embedding": settings.embedding_model,
    }

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                f"{settings.ollama_base_url}/api/tags"
            )

            response.raise_for_status()

            data = response.json()

        available_models = {
            model["name"]
            for model in data.get("models", [])
        }

        model_status = {
            role: {
                "name": model_name,
                "available": model_name in available_models,
            }
            for role, model_name in required_models.items()
        }

        return {
            "backend": "online",
            "ollama": {
                "status": "online",
                "models": model_status,
            },
        }

    except (httpx.HTTPError, KeyError):
        return {
            "backend": "online",
            "ollama": {
                "status": "offline",
                "models": {},
            },
        }


app.include_router(workspace_router)

app.include_router(files_router)

app.include_router(
    agent_router
)

app.include_router(
    terminal_router
)

app.include_router(
    git_router
)

app.include_router(
    repository_router
)

app.include_router(
    desktop_router
)

app.include_router(
    vision_router
)

app.include_router(
    voice_router
)

app.include_router(
    permissions_router
)

app.include_router(
    memory_router
)

app.include_router(
    guardrails_router
)

app.include_router(
    audit_router
)