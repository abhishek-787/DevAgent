export {};


declare global {
  type RequiredModelStatus = {
    name: string;
    available: boolean;
  };


  type SystemStatus = {
    backend: string;

    ollama: {
      status: string;

      models: Record<
        string,
        RequiredModelStatus
      >;
    };
  };


  type WorkspaceInfo = {
    active: boolean;
    name: string | null;
    path: string | null;
  };


  type AgentStreamEventType =
    | "task_started"
    | "tool_requested"
    | "tool_completed"
    | "agent_message"
    | "approval_required"
    | "approval_decision"
    | "task_completed"
    | "error";


  type AgentApprovalTool = {
    tool_name: string;

    arguments?: Record<
      string,
      unknown
    >;

    category?: string;

    requires_approval?: boolean;

    description?: string;
  };


  type AgentApproval = {
    type?: string;

    message?: string;

    tools?: AgentApprovalTool[];
  };


  type AgentStreamEvent = {
    type: AgentStreamEventType;

    thread_id?: string;

    message?: string;

    tool?: string;

    arguments?: Record<
      string,
      unknown
    >;

    tool_call_id?: string;

    result_preview?: string;

    content?: string;

    approval?: AgentApproval;

    approved?: boolean;

    answer?: string;

    tools_used?: string[];

    tool_rounds?: number;

    failed_test_runs?: number;

    error_type?: string;
  };

  type PersistedChatMessage = {
  id: string;

  thread_id: string;

  role:
    | "user"
    | "agent";

  content: string;

  created_at: string;
};


type ConversationHistory = {
  count: number;

  messages:
    PersistedChatMessage[];
};

type VoiceTranscriptionResult = {
  text: string;

  language?: string;

  language_probability?:
    number;
};

type GitChangedFile = {
  status: string;
  path: string;
};


  interface Window {
    codingAgent: {
      getSystemStatus: () =>
        Promise<{
          ok: boolean;

          data?: SystemStatus;

          error?: string;
        }>;


      openWorkspace: () =>
        Promise<{
          ok: boolean;

          canceled?: boolean;

          data?: WorkspaceInfo;

          error?: string;
        }>;


      getCurrentWorkspace: () =>
        Promise<{
          ok: boolean;

          data?: WorkspaceInfo;

          error?: string;
        }>;

        getConversationHistory: () =>
        Promise<{
          ok: boolean;

          data?:
            ConversationHistory;

          error?: string;
        }>;

      openWorkspaceInVSCode: () =>
        Promise<{
          ok: boolean;

          data?: {
            opened: boolean;

            editor: string;

            workspace: string;
          };

          error?: string;
        }>;

        getGitDiff: () =>
        Promise<{
          ok: boolean;

          data?: {
            diff: string;
          };

          error?: string;
        }>;

        getGitStatus: () =>
          Promise<{
            ok: boolean;

            data?: {
              files:
                GitChangedFile[];
            };

            error?: string;
          }>;

        transcribeVoice: (
        audioBuffer:
          ArrayBuffer,

        mimeType:
          string
      ) =>
        Promise<{
          ok: boolean;

          data?:
            VoiceTranscriptionResult;

          error?: string;
        }>;


      startAgentStream: (
        message: string
      ) => void;

      resumeAgentStream: (
      threadId: string,
      approved: boolean
    ) => void;

      onAgentStreamEvent: (
        callback: (
          event: AgentStreamEvent
        ) => void
      ) => () => void;
    };
  }
}