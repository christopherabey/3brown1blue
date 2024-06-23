"use client";

import React, { useState, useRef, RefObject, useEffect, useMemo } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import VideoStream from "@/components/videostream"; // Adjust the path as per your file structure
import { Progress } from "./ui/progress";
import { LoadingSpinner } from "./ui/LoadingSpinner";
import { useTheme } from "next-themes";
import { Chat } from "./Chat";

export function ClientComponent({ accessToken }: { accessToken: string }) {
  const textareaRef: RefObject<HTMLTextAreaElement> = useRef(null);
  const [videoID, setVideoID] = useState<string>("");
  const [emotions, setEmotions] = useState<string>(""); // string of comma-separated emotions
  const [progress, setProgress] = useState<number | null>(null);
  const progressInterval = useRef<NodeJS.Timeout | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const { setTheme } = useTheme();

  return (
    <div className="mx-auto bg-black">
      <Chat accessToken={accessToken} />
    </div>
  );
}

function SendIcon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m22 2-7 20-4-9-9-4Z" />
      <path d="M22 2 11 13" />
    </svg>
  );
}

const VideoIcon = (props: any) => {
  const { stroke = "currentColor" } = props; // Default stroke color is set to "currentColor" if not provided

  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke={stroke} // Use the stroke color from props
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {stroke === "red" ? (
        <>
          <line x1="1" y1="1" x2="23" y2="23" />
          <path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5" />
          <rect x="2" y="6" width="14" height="12" rx="2" />
        </>
      ) : (
        <>
          <path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5" />
          <rect x="2" y="6" width="14" height="12" rx="2" />
        </>
      )}
    </svg>
  );
};

export default ClientComponent;
