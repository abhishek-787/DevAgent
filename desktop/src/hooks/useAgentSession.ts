import {
  useEffect,
  useMemo,
  useState,
} from "react";

import type {
  AgentChatMessage,
  AgentStreamEvent,
  AgentTaskStatus,
  PendingApproval,
} from "../types/agent";

import {
  buildTaskActivities,
  getChangedFiles,
} from "../utils/agentActivity";


function createMessageId() {
  return (
    `${Date.now()}-` +
    Math.random()
      .toString(16)
      .slice(2)
  );
}


export function useAgentSession(
    workspace:
    WorkspaceInfo | null
) {
  const [
    events,
    setEvents,
  ] = useState<
    AgentStreamEvent[]
  >([]);

  const [
  historyLoading,
  setHistoryLoading,
] = useState(false);

  const [
    messages,
    setMessages,
  ] = useState<
    AgentChatMessage[]
  >([]);

  const [
    currentTask,
    setCurrentTask,
  ] = useState<
    string | null
  >(null);

  const [
    taskStatus,
    setTaskStatus,
  ] = useState<
    AgentTaskStatus
  >("idle");

  const [
    pendingApproval,
    setPendingApproval,
  ] = useState<
    PendingApproval | null
  >(null);

  const [
    approvalSubmitting,
    setApprovalSubmitting,
  ] = useState(false);

  useEffect(() => {
  let cancelled = false;


  async function loadHistory() {
    if (
      !workspace?.active
    ) {
      setMessages([]);

      setCurrentTask(
        null
      );

      setEvents([]);

      setTaskStatus(
        "idle"
      );

      return;
    }


    setHistoryLoading(
      true
    );

    try {
      const result =
        await window
          .codingAgent
          .getConversationHistory();


      if (
        cancelled
      ) {
        return;
      }


      if (
        result.ok &&
        result.data
      ) {
        setMessages(
          result.data.messages.map(
            (message) => ({
              id:
                message.id,

              role:
                message.role,

              content:
                message.content,
            })
          )
        );
      }
    } finally {
      if (!cancelled) {
        setHistoryLoading(
          false
        );
      }
    }
  }


  loadHistory();


  return () => {
    cancelled = true;
  };
}, [
  workspace?.path,
]);

  useEffect(() => {
    const unsubscribe =
      window.codingAgent
        .onAgentStreamEvent(
          (
            event:
              AgentStreamEvent
          ) => {
            setEvents(
              (current) => [
                ...current,
                event,
              ]
            );


                        if (
            event.type ===
            "agent_message"
            ) {
            const content =
                event.content;

            if (content) {
                setMessages(
                (current) => [
                    ...current,
                    {
                    id:
                        createMessageId(),

                    role:
                        "agent",

                    content,
                    },
                ]
                );
            }
            }


            if (
              event.type ===
              "approval_required"
            ) {
              if (
                event.thread_id &&
                event.approval
              ) {
                setPendingApproval(
                  {
                    threadId:
                      event.thread_id,

                    approval:
                      event.approval,
                  }
                );
              }

              setTaskStatus(
                "waiting_approval"
              );
            }


            if (
              event.type ===
              "approval_decision"
            ) {
              setPendingApproval(
                null
              );

              setApprovalSubmitting(
                false
              );

              setTaskStatus(
                "running"
              );
            }


            if (
              event.type ===
              "task_completed"
            ) {
              setTaskStatus(
                "completed"
              );

              setPendingApproval(
                null
              );

              setApprovalSubmitting(
                false
              );
            }


            if (
              event.type ===
              "error"
            ) {
              setTaskStatus(
                "error"
              );

              setApprovalSubmitting(
                false
              );
            }
          }
        );


    return () => {
      unsubscribe();
    };
  }, []);


  function startTask(
    message: string
  ): boolean {
    const cleaned =
      message.trim();

    if (
      !cleaned ||
      taskStatus ===
        "running" ||
      taskStatus ===
        "waiting_approval"
    ) {
      return false;
    }

    setCurrentTask(
      cleaned
    );

    setEvents([]);

    setPendingApproval(
      null
    );

    setTaskStatus(
      "running"
    );

    setMessages(
      (current) => [
        ...current,

        {
          id:
            createMessageId(),

          role:
            "user",

          content:
            cleaned,
        },
      ]
    );

    window.codingAgent
      .startAgentStream(
        cleaned
      );

    return true;
  }


  function submitApproval(
    approved: boolean
  ) {
    if (
      !pendingApproval ||
      approvalSubmitting
    ) {
      return;
    }

    setApprovalSubmitting(
      true
    );

    window.codingAgent
      .resumeAgentStream(
        pendingApproval
          .threadId,

        approved
      );
  }


  const activities =
    useMemo(
      () =>
        buildTaskActivities(
          events
        ),
      [events]
    );


  const changedFiles =
    useMemo(
      () =>
        getChangedFiles(
          events
        ),
      [events]
    );


  const latestActivity =
    activities.length > 0
      ? activities[
          activities.length - 1
        ]
      : null;


  return {
    events,
    messages,

    currentTask,
    taskStatus,

    activities,
    changedFiles,
    latestActivity,

    pendingApproval,
    approvalSubmitting,

    historyLoading,

    startTask,
    submitApproval,
  };
}


export type AgentSession =
  ReturnType<
    typeof useAgentSession
  >;