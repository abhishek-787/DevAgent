import {
  useEffect,
  useRef,
} from "react";

import type {
  AgentSession,
} from "../../hooks/useAgentSession";

import {
  ApprovalCard,
} from "./ApprovalCard";


type Props = {
  session: AgentSession;
};


export function AgentConversation({
  session,
}: Props) {
  const bottomRef =
    useRef<HTMLDivElement>(
      null
    );


  useEffect(() => {
    bottomRef.current
      ?.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
  }, [
    session.messages,
    session.taskStatus,
    session.pendingApproval,
    session.latestActivity,
  ]);


  return (
    <div
      className="agent-conversation"
    >
      {session.historyLoading && (
        <div
          className="agent-history-loading"
        >
          Loading conversation...
        </div>
      )}
      {!session.historyLoading && session.messages.length === 0 && (
        <div
          className="agent-welcome"
        >
          <strong>
            Ready to help.
          </strong>

          <p>
            Ask DevAgent to
            inspect, modify,
            test, or explain
            your codebase.
          </p>
        </div>
      )}


      {session.messages.map(
        (message) => (
          <div
            key={message.id}
            className={
              `chat-message chat-message--${message.role}`
            }
          >
            <span
              className="chat-message__role"
            >
              {message.role ===
              "user"
                ? "You"
                : "DevAgent"}
            </span>

            <div
              className="chat-message__content"
            >
              {message.content}
            </div>
          </div>
        )
      )}


      {session.taskStatus ===
        "running" && (
        <div
          className="agent-working"
        >
          <span
            className="agent-working__dot"
          />

          <span>
            {session.latestActivity
              ?.label ??
              "Working on your task"}
          </span>
        </div>
      )}


      <ApprovalCard
        session={session}
      />


      <div
        ref={bottomRef}
        className="conversation-bottom"
      />
    </div>
  );
}