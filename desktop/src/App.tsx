import { useEffect, useState } from "react";
import "./App.css";
import {AgentPanel} from "./components/agent/AgentPanel";
import {useAgentSession} from "./hooks/useAgentSession";

import { CurrentTaskPanel} from "./components/agent/CurrentTaskPanel";

import { DiffModal} from "./components/diff/DiffModal";

function App() {
  const [status, setStatus] =
    useState<SystemStatus | null>(null);

  const [connected, setConnected] =
    useState(false);

  const [workspace, setWorkspace] =
    useState<WorkspaceInfo | null>(null);

  const [workspaceError, setWorkspaceError] =
    useState<string | null>(null);
  
    const [diffOpen,setDiffOpen,] = useState(false);

const [
  diffText,
  setDiffText,
] = useState("");

const [
  diffLoading,
  setDiffLoading,
] = useState(false);

const [
  diffError,
  setDiffError,
] = useState<
  string | null
>(null);

const [
  gitChangedFiles,
  setGitChangedFiles,
] = useState<
  GitChangedFile[]
>([]);

  const agentSession = useAgentSession(
    workspace
  );


  const refreshStatus = async () => {
    try {
      const result =
        await window.codingAgent.getSystemStatus();

      if (result.ok && result.data) {
        setStatus(result.data);
        setConnected(true);
      } else {
        setConnected(false);
      }
    } catch {
      setConnected(false);
    }
  };


  const loadCurrentWorkspace = async () => {
    try {
      const result =
        await window.codingAgent.getCurrentWorkspace();

      if (
        result.ok &&
        result.data?.active
      ) {
        setWorkspace(result.data);
      }
    } catch {
    }
  };


  const handleOpenProject = async () => {
    setWorkspaceError(null);

    try {
      const result =
        await window.codingAgent.openWorkspace();

      if (result.canceled) {
        return;
      }

      if (result.ok && result.data) {
        setWorkspace(result.data);
        return;
      }

      setWorkspaceError(
        result.error ??
          "Unable to open project."
      );
    } catch {
      setWorkspaceError(
        "Unable to open project."
      );
    }
  };


  useEffect(() => {
    refreshStatus();
    loadCurrentWorkspace();

    const timer = setInterval(
      refreshStatus,
      5000
    );

    return () => clearInterval(timer);
  }, []);

  const handleOpenVSCode = async () => {
  try {
    const result =
      await window.codingAgent
        .openWorkspaceInVSCode();

    if (!result.ok) {
      setWorkspaceError(
        result.error ??
          "Unable to open VS Code."
      );
    }
  } catch {
    setWorkspaceError(
      "Unable to open VS Code."
    );
  }
};

async function handleViewDiff() {
  setDiffOpen(true);
  setDiffLoading(true);
  setDiffError(null);

  try {
    const result =
      await window
        .codingAgent
        .getGitDiff();

    if (
      result.ok &&
      result.data
    ) {
      setDiffText(
      typeof result.data.diff ===
        "string"
        ? result.data.diff
        : ""
    );
    } else {
      setDiffError(
        result.error ??
          "Unable to load diff."
      );
    }
  } catch {
    setDiffError(
      "Unable to load diff."
    );
  } finally {
    setDiffLoading(false);
  }
}

async function refreshGitStatus() {
  if (!workspace?.active) {
    setGitChangedFiles([]);
    return;
  }

  try {
    const result =
      await window
        .codingAgent
        .getGitStatus();

    if (
      result.ok &&
      result.data
    ) {
      setGitChangedFiles(
        result.data.files
      );
    }
  } catch {

  }
}

useEffect(() => {
  void refreshGitStatus();
}, [
  workspace?.path,
  agentSession.taskStatus,
]);

  return (
    <div className="app">

      {/* MAIN WORKSPACE */}
      <main className="workspace">

        <header className="title-bar">
          <div>
            <strong>DevAgent</strong>
          </div>

          <div className="title-actions">
            <button
              className="settings-button"
              title="Settings"
            >
              ⚙
            </button>
          </div>
        </header>


        <section className="workspace-content">

          {!workspace?.active ? (
            <div className="welcome-card">

              <span className="eyebrow">
                WORKSPACE
              </span>

              <h1>No project selected</h1>

              <p>
                Open a local development project
                to start using DevAgent.
              </p>

              <button
                className="primary-button"
                onClick={handleOpenProject}
              >
                Open Project
              </button>

              {workspaceError && (
                <p className="workspace-error">
                  {workspaceError}
                </p>
              )}

            </div>
          ) : (
            <div className="project-workspace">

              <section className="project-header">

                <span className="eyebrow">
                  ACTIVE WORKSPACE
                </span>

                <h1>{workspace.name}</h1>

                <p className="workspace-path">
                  {workspace.path}
                </p>

                <button
                  className="secondary-button"
                  onClick={handleOpenProject}
                >
                  Change Project
                </button>

                <button
                  className="secondary-button"
                  onClick={handleOpenVSCode}
                >
                  Open in VS Code
                </button>

              </section>


              <section className="task-section">
                <CurrentTaskPanel session={agentSession}/>
              </section>


              <section className="changed-files-section">
              <div className="section-heading">
                <span className="eyebrow">
                  CHANGED FILES
                </span>

                <button
                  className="text-button"
                  disabled={
                    gitChangedFiles.length === 0
                  }
                  onClick={handleViewDiff}
                >
                  View Diff
                </button>
              </div>


              {gitChangedFiles.length === 0 ? (
                <p className="empty-text">
                  No Git changes.
                </p>
              ) : (
                <div className="changed-file-list">
                  {gitChangedFiles.map(
                    (file) => (
                      <div
                        className="changed-file"
                        key={file.path}
                      >
                        <span
                          className="changed-file__status"
                        >
                          {file.status}
                        </span>

                        <span>
                          {file.path}
                        </span>
                      </div>
                    )
                  )}
                </div>
              )}
            </section>

            </div>
          )}

        </section>


        <footer className="status-bar">

          <span>
            Backend{" "}
            <strong>
              {connected
                ? "● Online"
                : "● Starting..."}
            </strong>
          </span>

          <span>
            Ollama{" "}
            <strong>
              {status?.ollama.status ===
              "online"
                ? "● Online"
                : "● Offline"}
            </strong>
          </span>

        </footer>

      </main>
      <AgentPanel
  connected={connected}
  workspace={workspace}
  session={agentSession}/>

  <DiffModal
  open={diffOpen}
  diff={diffText}
  loading={diffLoading}
  error={diffError}
  onClose={() =>
    setDiffOpen(false)
  }
/>

    </div>
  );
}


export default App;