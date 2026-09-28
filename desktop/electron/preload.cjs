const {
  contextBridge,
  ipcRenderer,
} = require("electron");


contextBridge.exposeInMainWorld(
  "codingAgent",
  {
    getSystemStatus: () =>
      ipcRenderer.invoke(
        "backend:get-status"
      ),

    openWorkspace: () =>
      ipcRenderer.invoke(
        "workspace:open"
      ),

    getCurrentWorkspace: () =>
      ipcRenderer.invoke(
        "workspace:get-current"
      ),
    openWorkspaceInVSCode: () =>
      ipcRenderer.invoke(
      "workspace:open-vscode"
  ),

  getConversationHistory: () =>
  ipcRenderer.invoke(
    "agent:conversation:get"
  ),

  getGitDiff: () =>
  ipcRenderer.invoke(
    "git:get-diff"
  ),

  getGitStatus: () =>
  ipcRenderer.invoke(
    "git:get-status"
  ),

  startAgentStream: (
  message
) => {
  ipcRenderer.send(
    "agent:stream:start",
    message
  );
},

resumeAgentStream: (
  threadId,
  approved
) => {
  ipcRenderer.send(
    "agent:approval:start",
    {
      threadId,
      approved,
    }
  );
},


onAgentStreamEvent: (
  callback
) => {
  const listener = (
    _event,
    payload
  ) => {
    callback(
      payload
    );
  };

  ipcRenderer.on(
    "agent:stream:event",
    listener
  );

  return () => {
    ipcRenderer.removeListener(
      "agent:stream:event",
      listener
    );
  };
},
  }
);