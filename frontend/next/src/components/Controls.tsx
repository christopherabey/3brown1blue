// ./components/Controls.tsx
"use client";
import { useVoice, VoiceReadyState } from "@humeai/voice-react";
export default function Controls() {
  const { connect, disconnect, readyState } = useVoice();

  if (readyState === VoiceReadyState.OPEN) {
    return (
      <button
        onClick={() => {
          disconnect();
        }}
      >
        End Session
      </button>
    );
  }

  return (
    <button
      onClick={() => {
        connect()
          .then(() => {
            /* handle success */
            console.log("Voice provider connected")
          })
          .catch(() => {
            /* handle error */
            console.log("Voice provider connection failed")

          });
      }}
    >
      Start Session
    </button>
  );
}
