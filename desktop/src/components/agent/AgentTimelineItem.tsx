import type {
  AgentStreamEvent,
} from "../../types/agent";


type AgentTimelineItemProps = {
  event:
    AgentStreamEvent;
};


function getEventTitle(
  event:
    AgentStreamEvent
): string {
  switch (
    event.type
  ) {
    case "task_started":
      return "Task started";

    case "tool_requested":
      return event.tool
        ? `Running ${event.tool}`
        : "Running tool";

    case "tool_completed":
      return event.tool
        ? `${event.tool} completed`
        : "Tool completed";

    case "agent_message":
      return "DevAgent";

    case "approval_required":
      return "Approval required";

    case "approval_decision":
      return event.approved
        ? "Action approved"
        : "Action rejected";

    case "task_completed":
      return "Task completed";

    case "error":
      return "Error";

    default:
      return "Agent event";
  }
}


export function AgentTimelineItem({
  event,
}: AgentTimelineItemProps) {
  return (
    <div
      className={
        `agent-event agent-event--${event.type}`
      }
    >
      <div
        className="agent-event__marker"
      />

      <div
        className="agent-event__content"
      >
        <div
          className="agent-event__title"
        >
          {
            getEventTitle(
              event
            )
          }
        </div>


        {event.type ===
          "tool_requested" &&
          event.arguments && (
            <details
              className="agent-event__details"
            >
              <summary>
                Details
              </summary>

              <pre>
                {JSON.stringify(
                  event.arguments,
                  null,
                  2
                )}
              </pre>
            </details>
          )}


        {event.type ===
          "tool_completed" &&
          event.result_preview && (
            <details
              className="agent-event__details"
            >
              <summary>
                Result
              </summary>

              <pre>
                {
                  event.result_preview
                }
              </pre>
            </details>
          )}


        {event.type ===
          "agent_message" &&
          event.content && (
            <p
              className="agent-event__message"
            >
              {
                event.content
              }
            </p>
          )}


        {event.type ===
          "approval_required" && (
            <p
              className="agent-event__message"
            >
              DevAgent is waiting
              for your permission
              before continuing.
            </p>
          )}


        {event.type ===
          "error" &&
          event.message && (
            <p
              className="agent-event__message"
            >
              {
                event.message
              }
            </p>
          )}
      </div>
    </div>
  );
}