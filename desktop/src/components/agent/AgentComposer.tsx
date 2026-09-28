import {
  useEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";



import type {
  AgentSession,
} from "../../hooks/useAgentSession";


type Props = {
  connected: boolean;

  workspace:
    WorkspaceInfo | null;

  session:
    AgentSession;
};


export function AgentComposer({
  connected,
  workspace,
  session,
}: Props) {
  const [
    input,
    setInput,
  ] = useState("");

  const textareaRef =
    useRef<HTMLTextAreaElement>(
      null
    );

    const [
  isRecording,
  setIsRecording,
] = useState(false);

const [
  isTranscribing,
  setIsTranscribing,
] = useState(false);

const [
  voiceError,
  setVoiceError,
] = useState<
  string | null
>(null);

const mediaRecorderRef =
  useRef<
    MediaRecorder | null
  >(null);

const mediaStreamRef =
  useRef<
    MediaStream | null
  >(null);

const audioChunksRef =
  useRef<Blob[]>([]);

  const busy =
    session.taskStatus ===
      "running" ||
    session.taskStatus ===
      "waiting_approval";


  const canSubmit =
    connected &&
    Boolean(
      workspace?.active
    ) &&
    !busy &&
    Boolean(
      input.trim()
    );


  useEffect(() => {
    const textarea =
      textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height =
      "auto";

    textarea.style.height =
      `${Math.min(
        textarea.scrollHeight,
        140
      )}px`;
  }, [input]);


  function submit() {
    if (!canSubmit) {
      return;
    }

    const started =
      session.startTask(
        input
      );

    if (started) {
      setInput("");
    }
  }


  function handleKeyDown(
    event:
      KeyboardEvent<
        HTMLTextAreaElement
      >
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      submit();
    }
  }

  async function startRecording() {
  try {
    setVoiceError(
      null
    );


    const stream =
      await navigator
        .mediaDevices
        .getUserMedia({
          audio: true,
        });


    mediaStreamRef.current =
      stream;


    const preferredType =
      MediaRecorder
        .isTypeSupported(
          "audio/webm"
        )
        ? "audio/webm"
        : "";


    const recorder =
      preferredType
        ? new MediaRecorder(
            stream,
            {
              mimeType:
                preferredType,
            }
          )
        : new MediaRecorder(
            stream
          );


    audioChunksRef.current =
      [];


    recorder.ondataavailable =
      (event) => {
        if (
          event.data.size > 0
        ) {
          audioChunksRef
            .current
            .push(
              event.data
            );
        }
      };


    recorder.onstop =
      async () => {
        const mimeType =
          recorder.mimeType ||
          "audio/webm";


        const blob =
          new Blob(
            audioChunksRef.current,
            {
              type:
                mimeType,
            }
          );


        mediaStreamRef
          .current
          ?.getTracks()
          .forEach(
            (track) =>
              track.stop()
          );


        mediaStreamRef.current =
          null;


        if (
          blob.size === 0
        ) {
          setVoiceError(
            "No audio was recorded."
          );

          return;
        }


        setIsTranscribing(
          true
        );


        try {
          const audioBuffer =
            await blob
              .arrayBuffer();


          const result =
            await window
              .codingAgent
              .transcribeVoice(
                audioBuffer,
                mimeType
              );


          if (
            result.ok &&
            result.data
              ?.text
          ) {
            setInput(
              result.data.text
            );
          } else {
            setVoiceError(
              result.error ??
                "Unable to transcribe audio."
            );
          }

        } catch {
          setVoiceError(
            "Unable to transcribe audio."
          );

        } finally {
          setIsTranscribing(
            false
          );
        }
      };


    mediaRecorderRef.current =
      recorder;


    recorder.start();


    setIsRecording(
      true
    );

  } catch {
    setVoiceError(
      "Microphone permission was denied or unavailable."
    );
  }
}

function stopRecording() {
  const recorder =
    mediaRecorderRef.current;


  if (
    recorder &&
    recorder.state !==
      "inactive"
  ) {
    recorder.stop();
  }


  setIsRecording(
    false
  );
}

function handleMicrophone() {
  if (
    isTranscribing ||
    busy
  ) {
    return;
  }


  if (isRecording) {
    stopRecording();
  } else {
    void startRecording();
  }
}

useEffect(() => {
  return () => {
    const recorder =
      mediaRecorderRef
        .current;

    if (
      recorder &&
      recorder.state !==
        "inactive"
    ) {
      recorder.stop();
    }


    mediaStreamRef.current
      ?.getTracks()
      .forEach(
        (track) =>
          track.stop()
      );
  };
}, []);

  return (
    <div
      className="agent-composer"
    >
      <div
        className="agent-composer__input"
      >
        <textarea
          ref={textareaRef}
          value={input}
          rows={1}
          placeholder={
            !workspace?.active
              ? "Open a project first..."
              : session.taskStatus ===
                  "waiting_approval"
                ? "Respond to the approval request first..."
                : "Ask DevAgent..."
          }
          disabled={
            !workspace?.active ||
            busy
          }
          onChange={(
            event
          ) => {
            setInput(
              event.target.value
            );
          }}
          onKeyDown={
            handleKeyDown
          }
        />


        <div
          className="agent-composer__actions"
        >
                      <button
              type="button"
              className={
                isRecording
                  ? "composer-action composer-action--recording"
                  : "composer-action"
              }
              disabled={
                busy ||
                isTranscribing ||
                !workspace?.active
              }
              onClick={
                handleMicrophone
              }
              title={
                isRecording
                  ? "Stop recording"
                  : "Voice input"
              }
            >
              {isTranscribing
                ? "…"
                : isRecording
                  ? "■"
                  : "🎤"}
            </button>

          <button
            type="button"
            className="composer-send"
            disabled={
              !canSubmit
            }
            onClick={
              submit
            }
            title="Send"
          >
            ➤
          </button>
        </div>
      </div>
      {isRecording && (
      <div className="voice-status">
        ● Recording — click stop
        when finished
      </div>
    )}

    {isTranscribing && (
      <div className="voice-status">
        Transcribing voice...
      </div>
    )}

    {voiceError && (
      <div className="voice-error">
        {voiceError}
      </div>
    )}
    </div>
  );
}