import type {
  AgentSession,
} from "../../hooks/useAgentSession";

import {
  AgentComposer,
} from "./AgentComposer";

import {
  AgentConversation,
} from "./AgentConversation";


type Props = {
  connected: boolean;

  workspace:
    WorkspaceInfo | null;

  session:
    AgentSession;
};


export function AgentPanel({
  connected,
  workspace,
  session,
}: Props) {
  function getStatusText() {
    switch (
      session.taskStatus
    ) {
      case "running":
        return "Working";

      case "waiting_approval":
        return (
          "Waiting for approval"
        );

      case "error":
        return "Error";

      default:
        return connected
          ? "Ready"
          : "Offline";
    }
  }


  return (
    <aside
      className="agent-panel"
    >
      <div
        className="agent-header"
      >
        <div>
          <span
            className="eyebrow"
          >
            CODING AGENT
          </span>

          <h2>
            DevAgent
          </h2>

          <span
            className="agent-status-text"
          >
            {getStatusText()}
          </span>
        </div>


        <span
          className="connection-dot"
          title={
            connected
              ? "Connected"
              : "Disconnected"
          }
        >
          {connected
            ? "●"
            : "○"}
        </span>
      </div>


      <AgentConversation
        session={session}
      />


      <AgentComposer
        connected={connected}
        workspace={workspace}
        session={session}
      />
    </aside>
  );
}