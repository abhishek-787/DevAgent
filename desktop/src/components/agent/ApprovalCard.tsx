import type {
  AgentSession,
} from "../../hooks/useAgentSession";

import {
  humanizeTool,
} from "../../utils/agentActivity";


type Props = {
  session:
    AgentSession;
};


export function ApprovalCard({
  session,
}: Props) {
  const pending =
    session.pendingApproval;

  if (!pending) {
    return null;
  }


  const tool =
    pending.approval
      .tools?.[0];

  const title =
    humanizeTool(
      tool?.tool_name,
      tool?.arguments
    );


  return (
    <div
      className="approval-card"
    >
      <span
        className="approval-card__eyebrow"
      >
        APPROVAL REQUIRED
      </span>

      <strong
        className="approval-card__title"
      >
        {title}
      </strong>

      {tool?.description && (
        <p
          className="approval-card__description"
        >
          {
            tool.description
          }
        </p>
      )}


      {tool?.arguments && (
        <details
          className="approval-card__details"
        >
          <summary>
            Review details
          </summary>

          <pre>
            {JSON.stringify(
              tool.arguments,
              null,
              2
            )}
          </pre>
        </details>
      )}


      <div
        className="approval-card__actions"
      >
        <button
          type="button"
          className="approval-reject"
          disabled={
            session
              .approvalSubmitting
          }
          onClick={() =>
            session
              .submitApproval(
                false
              )
          }
        >
          Reject
        </button>

        <button
          type="button"
          className="approval-approve"
          disabled={
            session
              .approvalSubmitting
          }
          onClick={() =>
            session
              .submitApproval(
                true
              )
          }
        >
          {session
            .approvalSubmitting
            ? "Submitting..."
            : "Approve"}
        </button>
      </div>
    </div>
  );
}