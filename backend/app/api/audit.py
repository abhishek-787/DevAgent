from fastapi import (
    APIRouter,
    HTTPException,
)

from app.memory.service import (
    list_audit_events,
)


router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)


@router.get(
    "/threads/{thread_id}"
)
def get_thread_audit(
    thread_id: str,
):
    try:
        events = list_audit_events(
            thread_id
        )

        return {
            "thread_id":
                thread_id,

            "count":
                len(events),

            "events": [
                {
                    "id":
                        event.id,

                    "event_type":
                        event.event_type,

                    "details":
                        event.details,

                    "created_at":
                        event.created_at,
                }
                for event
                in events
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc