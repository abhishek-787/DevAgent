const { app, BrowserWindow, ipcMain,dialog,session } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

let backendProcess = null;

const BACKEND_URL = "http://127.0.0.1:8000";

function startPackagedBackend() {
  const configDir = path.join(
    app.getPath("appData"),
    "DevAgent"
  );

  fs.mkdirSync(
    configDir,
    {
      recursive: true,
    }
  );

  const logPath = path.join(
    configDir,
    "backend.log"
  );

  const envPath = path.join(
    configDir,
    ".env"
  );

  const backendExe = path.join(
    process.resourcesPath,
    "backend",
    "devagent-backend",
    "devagent-backend.exe"
  );


  const writeLog = (
    message
  ) => {
    fs.appendFileSync(
      logPath,
      `${new Date().toISOString()} ${message}\n`
    );
  };


  writeLog(
    "startPackagedBackend called"
  );

  writeLog(
    `backendExe=${backendExe}`
  );

  writeLog(
    `backendExists=${fs.existsSync(
      backendExe
    )}`
  );

  writeLog(
    `envPath=${envPath}`
  );

  writeLog(
    `envExists=${fs.existsSync(
      envPath
    )}`
  );


  try {
    backendProcess = spawn(
      backendExe,
      [],
      {
        cwd: path.dirname(
          backendExe
        ),

        windowsHide: false,

        env: {
          ...process.env,

          DEVAGENT_ENV_FILE:
            envPath,
        },
      }
    );


    writeLog(
      `spawned pid=${backendProcess.pid}`
    );


    backendProcess.stdout?.on(
      "data",
      (data) => {
        writeLog(
          `[stdout] ${data.toString()}`
        );
      }
    );


    backendProcess.stderr?.on(
      "data",
      (data) => {
        writeLog(
          `[stderr] ${data.toString()}`
        );
      }
    );


    backendProcess.on(
      "error",
      (error) => {
        writeLog(
          `[error] ${error.message}`
        );
      }
    );


    backendProcess.on(
      "exit",
      (code, signal) => {
        writeLog(
          `[exit] code=${code}, signal=${signal}`
        );
      }
    );

  } catch (error) {
    writeLog(
      `[exception] ${
        error instanceof Error
          ? error.stack
          : String(error)
      }`
    );
  }
}




function startDevelopmentBackend() {
  const pythonPath =
    path.join(
      __dirname,
      "..",
      "..",
      "backend",
      ".venv",
      "Scripts",
      "python.exe"
    );


  const backendDirectory =
    path.join(
      __dirname,
      "..",
      "..",
      "backend"
    );


  backendProcess = spawn(
    pythonPath,
    [
      "-m",
      "uvicorn",
      "app.main:app",
      "--host",
      "127.0.0.1",
      "--port",
      "8000",
    ],
    {
      cwd: backendDirectory,
      windowsHide: true,
    }
  );


  backendProcess.stdout?.on(
    "data",
    (data) => {
      console.log(
        `[backend] ${data}`
      );
    }
  );


  backendProcess.stderr?.on(
    "data",
    (data) => {
      console.error(
        `[backend] ${data}`
      );
    }
  );
}



function getBackendDirectory() {
  return path.resolve(__dirname, "../../backend");
}


function getPythonExecutable(backendDirectory) {
  if (process.platform === "win32") {
    return path.join(
      backendDirectory,
      ".venv",
      "Scripts",
      "python.exe"
    );
  }

  return path.join(
    backendDirectory,
    ".venv",
    "bin",
    "python"
  );
}


function startBackend() {
  const configDir = path.join(
    app.getPath("appData"),
    "DevAgent"
  );

  fs.mkdirSync(
    configDir,
    {
      recursive: true,
    }
  );

  const logPath = path.join(
    configDir,
    "backend.log"
  );


  fs.appendFileSync(
    logPath,
    `${new Date().toISOString()} startBackend called, packaged=${app.isPackaged}\n`
  );


  if (app.isPackaged) {
    fs.appendFileSync(
      logPath,
      `${new Date().toISOString()} calling startPackagedBackend\n`
    );

    startPackagedBackend();

    return;
  }


  fs.appendFileSync(
    logPath,
    `${new Date().toISOString()} calling startDevelopmentBackend\n`
  );

  startDevelopmentBackend();
}


function stopBackend() {
  if (
    backendProcess &&
    !backendProcess.killed
  ) {
    backendProcess.kill();

    backendProcess = null;
  }
}

async function streamBackendEvents(
  endpoint,
  body,
  sendEvent
) {
  const response = await fetch(
    `${BACKEND_URL}${endpoint}`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(
        body
      ),
    }
  );

  if (!response.ok) {
    const errorText =
      await response.text();

    throw new Error(
      errorText ||
        `Backend returned ${response.status}`
    );
  }

  if (!response.body) {
    throw new Error(
      "Backend stream did not return a body."
    );
  }

  const reader =
    response.body.getReader();

  const decoder =
    new TextDecoder();

  let buffer = "";

  while (true) {
    const {
      done,
      value,
    } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(
      value,
      {
        stream: true,
      }
    );

    const lines =
      buffer.split("\n");

    buffer =
      lines.pop() ?? "";

    for (const line of lines) {
      const cleanedLine =
        line.trim();

      if (!cleanedLine) {
        continue;
      }

      sendEvent(
        JSON.parse(
          cleanedLine
        )
      );
    }
  }

  const remaining =
    buffer.trim();

  if (remaining) {
    sendEvent(
      JSON.parse(
        remaining
      )
    );
  }
}


function streamAgentTask(
  message,
  sendEvent
) {
  return streamBackendEvents(
    "/agent/stream",
    {
      message,
    },
    sendEvent
  );
}


function streamAgentApproval(
  threadId,
  approved,
  sendEvent
) {
  return streamBackendEvents(
    "/agent/approval/stream",
    {
      thread_id:
        threadId,

      approved,
    },
    sendEvent
  );
}

function createWindow() {
  const mainWindow =
    new BrowserWindow({
      width: 1400,
      height: 900,

      webPreferences: {
        preload: path.join(
          __dirname,
          "preload.cjs"
        ),

        contextIsolation: true,
        nodeIntegration: false,
      },
    });


  if (app.isPackaged) {
    mainWindow.loadFile(
      path.join(
        __dirname,
        "..",
        "dist",
        "index.html"
      )
    );
  } else {
    mainWindow.loadURL(
      "http://localhost:5173"
    );
  }
}


ipcMain.handle("backend:get-status", async () => {
  try {
    const response = await fetch(
      `${BACKEND_URL}/system/status`
    );

    if (!response.ok) {
      throw new Error(
        `Backend returned ${response.status}`
      );
    }

    const data = await response.json();

    return {
      ok: true,
      data,
    };
  } catch (error) {
    return {
      ok: false,
      error:
        error instanceof Error
          ? error.message
          : "Backend unavailable",
    };
  }
});


ipcMain.handle(
  "workspace:open",
  async () => {
    const result = await dialog.showOpenDialog({
      title: "Open Project",
      properties: ["openDirectory"],
    });

    if (
      result.canceled ||
      result.filePaths.length === 0
    ) {
      return {
        ok: false,
        canceled: true,
      };
    }

    const selectedPath = result.filePaths[0];

    try {
      const response = await fetch(
        `${BACKEND_URL}/workspace/open`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            path: selectedPath,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        return {
          ok: false,
          error:
            data.detail ??
            "Failed to open workspace.",
        };
      }

      return {
        ok: true,
        data,
      };
    } catch (error) {
      return {
        ok: false,
        error:
          error instanceof Error
            ? error.message
            : "Backend unavailable.",
      };
    }
  }
);

ipcMain.handle(
  "workspace:get-current",
  async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/workspace/current`
      );

      const data = await response.json();

      if (!response.ok) {
        return {
          ok: false,
          error: "Failed to get workspace.",
        };
      }

      return {
        ok: true,
        data,
      };
    } catch (error) {
      return {
        ok: false,
        error:
          error instanceof Error
            ? error.message
            : "Backend unavailable.",
      };
    }
  }
);

ipcMain.handle(
  "workspace:open-vscode",
  async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/workspace/open-vscode`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        return {
          ok: false,
          error:
            data.detail ??
            "Failed to open VS Code.",
        };
      }

      return {
        ok: true,
        data,
      };
    } catch (error) {
      return {
        ok: false,
        error:
          error instanceof Error
            ? error.message
            : "Backend unavailable.",
      };
    }
  }
);

ipcMain.handle(
  "git:get-status",
  async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/git/status`
      );

      const data =
        await response.json();

      if (!response.ok) {
        return {
          ok: false,
          error:
            data.detail ??
            "Unable to load Git status.",
        };
      }

      return {
        ok: true,
        data,
      };

    } catch (error) {
      return {
        ok: false,

        error:
          error instanceof Error
            ? error.message
            : "Backend unavailable.",
      };
    }
  }
);

ipcMain.on(
  "agent:stream:start",
  async (
    event,
    message
  ) => {
    try {
      const cleanedMessage =
        message?.trim();

      if (!cleanedMessage) {
        event.sender.send(
          "agent:stream:event",
          {
            type: "error",
            message:
              "Task message cannot be empty.",
          }
        );

        return;
      }

      await streamAgentTask(
        cleanedMessage,
        (payload) => {
          if (
            !event.sender.isDestroyed()
          ) {
            event.sender.send(
              "agent:stream:event",
              payload
            );
          }
        }
      );
    } catch (error) {
      if (
        !event.sender.isDestroyed()
      ) {
        event.sender.send(
          "agent:stream:event",
          {
            type: "error",

            error_type:
              "ElectronStreamError",

            message:
              error instanceof Error
                ? error.message
                : String(error),
          }
        );
      }
    }
  }
);


ipcMain.on(
  "agent:approval:start",
  async (
    event,
    payload
  ) => {
    try {
      const threadId =
        payload?.threadId;

      const approved =
        payload?.approved;

      if (
        !threadId ||
        typeof approved !==
          "boolean"
      ) {
        throw new Error(
          "Invalid approval request."
        );
      }

      await streamAgentApproval(
        threadId,
        approved,
        (streamEvent) => {
          if (
            !event.sender
              .isDestroyed()
          ) {
            event.sender.send(
              "agent:stream:event",
              streamEvent
            );
          }
        }
      );
    } catch (error) {
      if (
        !event.sender
          .isDestroyed()
      ) {
        event.sender.send(
          "agent:stream:event",
          {
            type: "error",

            error_type:
              "ElectronApprovalError",

            message:
              error instanceof Error
                ? error.message
                : String(error),
          }
        );
      }
    }
  }
);

ipcMain.handle(
  "agent:conversation:get",
  async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/memory/conversation?limit=20`
      );

      const data =
        await response.json();

      if (!response.ok) {
        return {
          ok: false,

          error:
            data.detail ??
            "Failed to load conversation history.",
        };
      }

      return {
        ok: true,
        data,
      };
    } catch (error) {
      return {
        ok: false,

        error:
          error instanceof Error
            ? error.message
            : "Backend unavailable.",
      };
    }
  }
);

ipcMain.handle(
  "git:get-diff",
  async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/git/diff`
      );

      const data =
        await response.json();

      if (!response.ok) {
        return {
          ok: false,
          error:
            data.detail ??
            "Unable to load Git diff.",
        };
      }

      return {
        ok: true,
        data,
      };
    } catch (error) {
      return {
        ok: false,

        error:
          error instanceof Error
            ? error.message
            : "Backend unavailable.",
      };
    }
  }
);

ipcMain.handle(
  "voice:transcribe",
  async (
    _event,
    payload
  ) => {
    try {
      const {
        audioBuffer,
        mimeType,
      } = payload;

      if (!audioBuffer) {
        throw new Error(
          "Audio data is missing."
        );
      }


      const buffer =
        Buffer.from(
          audioBuffer
        );


      const type =
        mimeType ||
        "audio/webm";


      let extension =
        "webm";

      if (
        type.includes(
          "wav"
        )
      ) {
        extension = "wav";
      } else if (
        type.includes(
          "mp3"
        )
      ) {
        extension = "mp3";
      } else if (
        type.includes(
          "ogg"
        )
      ) {
        extension = "ogg";
      }


      const formData =
        new FormData();


      formData.append(
        "file",

        new Blob(
          [buffer],
          {
            type,
          }
        ),

        `voice.${extension}`
      );


      const response =
        await fetch(
          `${BACKEND_URL}/voice/transcribe`,
          {
            method:
              "POST",

            body:
              formData,
          }
        );


      const data =
        await response.json();


      if (!response.ok) {
        return {
          ok: false,

          error:
            data.detail ??
            "Voice transcription failed.",
        };
      }


      return {
        ok: true,
        data,
      };

    } catch (error) {
      return {
        ok: false,

        error:
          error instanceof Error
            ? error.message
            : "Voice transcription failed.",
      };
    }
  }
);

app.whenReady().then(() => {
  const debugDir = path.join(
  app.getPath("appData"),
  "DevAgent"
);

fs.mkdirSync(
  debugDir,
  {
    recursive: true,
  }
);

fs.writeFileSync(
  path.join(
    debugDir,
    "electron-startup.txt"
  ),
  [
    `Started: ${new Date().toISOString()}`,
    `isPackaged: ${app.isPackaged}`,
    `resourcesPath: ${process.resourcesPath}`,
    `appPath: ${app.getAppPath()}`,
  ].join("\n")
);
  session.defaultSession
  .setPermissionRequestHandler(
    (
      _webContents,
      permission,
      callback
    ) => {
      if (
        permission ===
        "media"
      ) {
        callback(true);
        return;
      }

      callback(false);
    }
  );
  startBackend();
  createWindow();
});


app.on("before-quit", () => {
  stopBackend();
});


app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});