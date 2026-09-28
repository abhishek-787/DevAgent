import type {AgentStreamEvent,TaskActivity} from "../types/agent";


function getPath(
  args:
    Record<
      string,
      unknown
    > | undefined
): string | null {
  if (!args) {
    return null;
  }

  const value =
    args.path ??
    args.test_path;

  return typeof value ===
    "string"
    ? value
    : null;
}


export function humanizeTool(
  tool:
    string | undefined,
  args?:
    Record<
      string,
      unknown
    >
): string {
  const path =
    getPath(args);

  switch (tool) {
    case "get_workspace_info":
      return (
        "Checking workspace"
      );

    case "list_directory":
      return path
        ? `Listing ${path}`
        : "Listing files";

    case "search_files":
      return (
        "Searching files"
      );

    case "search_text":
      return (
        "Searching source code"
      );

    case "semantic_code_search":
      return (
        "Searching codebase"
      );

    case "read_file":
      return path
        ? `Reading ${path}`
        : "Reading file";

    case "create_directory":
      return path
        ? `Creating ${path}`
        : "Creating directory";

    case "create_file":
      return path
        ? `Creating ${path}`
        : "Creating file";

    case "edit_file":
      return path
        ? `Editing ${path}`
        : "Editing file";

    case "run_tests":
      return path &&
        path !== "."
        ? `Running tests: ${path}`
        : "Running tests";

    case "git_status":
      return (
        "Checking Git status"
      );

    case "git_diff":
      return (
        "Inspecting Git diff"
      );

    case "git_diff_file":
      return path
        ? `Inspecting diff for ${path}`
        : "Inspecting file diff";

    case "open_in_vscode":
      return (
        "Opening VS Code"
      );

    case "open_url":
      return (
        "Opening URL"
      );

    case "open_workspace_path":
      return path
        ? `Opening ${path}`
        : "Opening workspace item";

    case "reveal_in_explorer":
      return (
        "Revealing item in Explorer"
      );

    case "analyze_screen":
      return (
        "Analyzing screen"
      );

    default:
      return tool
        ? `Running ${tool}`
        : "Working";
  }
}

export function buildTaskActivities(
  events:
    AgentStreamEvent[]
): TaskActivity[] {
  const activities:
    TaskActivity[] = [];

  const byCallId =
    new Map<
      string,
      TaskActivity
    >();


  for (
    const event
    of events
  ) {
    if (
      event.type ===
      "tool_requested"
    ) {
      const id =
        event.tool_call_id ??
        `tool-${activities.length}`;

      const activity:
        TaskActivity = {
          id,
          tool:
            event.tool,

          label:
            humanizeTool(
              event.tool,
              event.arguments
            ),

          status:
            "running",
        };

      activities.push(
        activity
      );

      if (
        event.tool_call_id
      ) {
        byCallId.set(
          event.tool_call_id,
          activity
        );
      }
    }


    if (
      event.type ===
      "tool_completed"
    ) {
      let activity:
        TaskActivity |
        undefined;

      if (
        event.tool_call_id
      ) {
        activity =
          byCallId.get(
            event.tool_call_id
          );
      }

      if (!activity) {
        activity =
          [...activities]
            .reverse()
            .find(
              (item) =>
                item.tool ===
                  event.tool &&
                item.status ===
                  "running"
            );
      }

      if (activity) {
        activity.status =
          "completed";
      }
    }


    if (
      event.type ===
      "approval_required"
    ) {
      const tool =
        event.approval
          ?.tools?.[0]
          ?.tool_name;

      const activity =
        [...activities]
          .reverse()
          .find(
            (item) =>
              item.tool ===
                tool &&
              item.status ===
                "running"
          );

      if (activity) {
        activity.status =
          "waiting";
      }
    }


    if (
      event.type ===
      "approval_decision"
    ) {
      const activity =
        [...activities]
          .reverse()
          .find(
            (item) =>
              item.status ===
              "waiting"
          );

      if (activity) {
        activity.status =
          event.approved
            ? "running"
            : "rejected";
      }
    }
  }


  return activities;
}

export function getChangedFiles(
  events:
    AgentStreamEvent[]
): string[] {
  const requested =
    new Map<
      string,
      AgentStreamEvent
    >();

  const files =
    new Set<string>();


  for (
    const event
    of events
  ) {
    if (
      event.type ===
        "tool_requested" &&
      event.tool_call_id
    ) {
      requested.set(
        event.tool_call_id,
        event
      );
    }


    if (
      event.type ===
        "tool_completed" &&
      event.tool_call_id
    ) {
      const original =
        requested.get(
          event.tool_call_id
        );

      if (
        original?.tool !==
          "edit_file" &&
        original?.tool !==
          "create_file"
      ) {
        continue;
      }

      const path =
        original.arguments
          ?.path;

      if (
        typeof path ===
        "string"
      ) {
        files.add(
          path
        );
      }
    }
  }


  return [
    ...files,
  ];
}