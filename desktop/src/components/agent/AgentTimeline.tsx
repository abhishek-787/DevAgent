import {
  useEffect,
  useRef,
} from "react";

import type {
  AgentStreamEvent,
} from "../../types/agent";

import {
  AgentTimelineItem,
} from "./AgentTimelineItem";


type AgentTimelineProps = {
  events:
    AgentStreamEvent[];
};


export function AgentTimeline({
  events,
}: AgentTimelineProps) {
  const bottomRef =
    useRef<HTMLDivElement>(
      null
    );


  useEffect(() => {
    bottomRef.current
      ?.scrollIntoView({
        behavior:
          "smooth",

        block:
          "nearest",
      });
  }, [events]);


  if (
    events.length === 0
  ) {
    return (
      <div
        className="agent-timeline-empty"
      >
        <strong>
          Ready to help
        </strong>

        <span>
          Ask DevAgent to
          inspect, modify,
          test, or explain
          your project.
        </span>
      </div>
    );
  }


  return (
    <div
      className="agent-timeline"
    >
      {events.map(
        (
          event,
          index
        ) => (
          <AgentTimelineItem
            key={
              event.tool_call_id
              ??
              `${event.type}-${index}`
            }
            event={event}
          />
        )
      )}

      <div
        ref={bottomRef}
      />
    </div>
  );
}