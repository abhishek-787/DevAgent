import {
  useCallback,
  useEffect,
  useState,
} from "react";

import type {
  AgentStreamEvent,
} from "../types/agent";


export function useAgentStream() {
  const [
    events,
    setEvents,
  ] = useState<
    AgentStreamEvent[]
  >([]);

  const [
    isRunning,
    setIsRunning,
  ] = useState(false);


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
                "task_completed" ||
              event.type ===
                "approval_required" ||
              event.type ===
                "error"
            ) {
              setIsRunning(
                false
              );
            }
          }
        );

    return () => {
      unsubscribe();
    };
  }, []);


  const startTask =
    useCallback(
      (
        message: string
      ) => {
        const cleanedMessage =
          message.trim();

        if (
          !cleanedMessage ||
          isRunning
        ) {
          return false;
        }

        setEvents([]);

        setIsRunning(
          true
        );

        window.codingAgent
          .startAgentStream(
            cleanedMessage
          );

        return true;
      },
      [isRunning]
    );


  const clearEvents =
    useCallback(() => {
      setEvents([]);
    }, []);


  return {
    events,
    isRunning,
    startTask,
    clearEvents,
  };
}