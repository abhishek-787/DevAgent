export type AgentStreamEventType =
  | "task_started"
  | "tool_requested"
  | "tool_completed"
  | "agent_message"
  | "approval_required"
  | "approval_decision"
  | "task_completed"
  | "error";


export interface AgentStreamEvent {
  type: AgentStreamEventType;

  thread_id?: string;

  message?: string;

  tool?: string;

  arguments?: Record<string, unknown>;

  tool_call_id?: string;

  result_preview?: string;

  content?: string;

  approval?: {
    type?: string;
    message?: string;

    tools?: Array<{
      tool_name: string;
      arguments?: Record<string, unknown>;
      category?: string;
      requires_approval?: boolean;
      description?: string;
    }>;
  };

  approved?: boolean;

  answer?: string;

  tools_used?: string[];

  tool_rounds?: number;

  failed_test_runs?: number;

  error_type?: string;
}


export type AgentChatRole =
  | "user"
  | "agent";


export type AgentChatMessage = {
  id: string;

  role:
    AgentChatRole;

  content: string;
};


export type PendingApproval = {
  threadId: string;

  approval: NonNullable<
    AgentStreamEvent[
      "approval"
    ]
  >;
};


export type AgentTaskStatus =
  | "idle"
  | "running"
  | "waiting_approval"
  | "completed"
  | "error";


export type TaskActivityStatus =
  | "running"
  | "completed"
  | "waiting"
  | "rejected"
  | "failed";


export type TaskActivity = {
  id: string;

  tool?: string;

  label: string;

  status:
    TaskActivityStatus;
};