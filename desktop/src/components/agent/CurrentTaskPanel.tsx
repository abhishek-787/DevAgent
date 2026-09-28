import type {
  AgentSession,
} from "../../hooks/useAgentSession";


type Props = {
  session:
    AgentSession;
};


function getStatusText(
  session:
    AgentSession
) {
  switch (
    session.taskStatus
  ) {
    case "running":
      return "Working";

    case "waiting_approval":
      return (
        "Waiting for approval"
      );

    case "completed":
      return "Completed";

    case "error":
      return "Failed";

    default:
      return null;
  }
}


function getActivityIcon(
  status: string
) {
  switch (status) {
    case "completed":
      return "✓";

    case "waiting":
      return "⚠";

    case "rejected":
      return "×";

    case "failed":
      return "×";

    default:
      return "●";
  }
}


export function CurrentTaskPanel({
  session,
}: Props) {
  if (
    !session.currentTask
  ) {
    return (
      <section
        className="task-section"
      >
        <span
          className="eyebrow"
        >
          CURRENT TASK
        </span>

        <div
          className="empty-task"
        >
          <h3>
            No active task
          </h3>

          <p>
            Ask DevAgent to
            inspect, modify,
            test, or explain
            the current project.
          </p>
        </div>
      </section>
    );
  }


  return (
    <section
      className="task-section"
    >
      <div
        className="task-heading-row"
      >
        <span
          className="eyebrow"
        >
          CURRENT TASK
        </span>

        <span
          className={
            `task-status task-status--${session.taskStatus}`
          }
        >
          {
            getStatusText(
              session
            )
          }
        </span>
      </div>


      <h3
        className="task-title"
      >
        {
          session.currentTask
        }
      </h3>


      <div
        className="task-activity-list"
      >
        {session.activities.map(
          (activity) => (
            <div
              className={
                `task-activity task-activity--${activity.status}`
              }
              key={
                activity.id
              }
            >
              <span
                className="task-activity-icon"
              >
                {
                  getActivityIcon(
                    activity.status
                  )
                }
              </span>

              <span>
                {
                  activity.label
                }
              </span>
            </div>
          )
        )}
      </div>
    </section>
  );
}