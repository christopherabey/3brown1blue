// ./components/Controls.tsx
"use client";
import { useVoice, VoiceReadyState } from "@humeai/voice-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export default function Controls() {
  const [mic, setMic] = useState<boolean>(false);
  const { connect, disconnect, readyState } = useVoice();

  function handleMicClick() {
    setMic((prev) => !prev);
    connect()
      .then(() => {
        /* handle success */
        console.log("Voice provider connected");
      })
      .catch(() => {
        /* handle error */
        console.log("Voice provider connection failed");
      });
  }

  if (readyState === VoiceReadyState.OPEN) {
    return (
      <Button
        onClick={() => {
          disconnect();
        }}
        variant="ghost"
        size="icon"
        className="text-muted-foreground"
      >
        <MicIcon className="w-6 h-6" />
      </Button>
    );
  }

  return (
    <Button
      onClick={handleMicClick}
      variant="ghost"
      size="icon"
      className="text-muted-foreground"
    >
      <MicIcon className="w-6 h-6" stroke="red" />
    </Button>
  );
}

const MicIcon = (props: any) => {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke={props.stroke === "red" ? "red" : "currentColor"}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" x2="12" y1="19" y2="22" />
      {props.stroke === "red" && <line x1="1" y1="1" x2="23" y2="23" />}
    </svg>
  );
};
