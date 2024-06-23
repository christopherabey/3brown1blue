"use client";

import { useState, useRef, RefObject } from "react";
import { Textarea } from "@/components/ui/textarea";
import dynamic from "next/dynamic";
import { Button } from "@/components/ui/button";
import Message from "@/components/ui/message";
import VideoStream from "./videostream";

// Dynamically import the Webcam component for client-side rendering
// const Webcam = dynamic(() => import("@/components/webcam"), { ssr: false });

interface Message {
  avatarSrc: string;
  avatarFallback: string;
  author: string;
  text: string;
}

export function Page() {
  const [messages, setMessages] = useState<Message[]>([]);
  const textareaRef: RefObject<HTMLTextAreaElement> = useRef(null);

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendChatMessage();
    }
  }

  function sendChatMessage() {
    const textarea = textareaRef.current;

    if (textarea) {
      const messageText = textarea.value;

      if (messageText.trim() === "") {
        return;
      }

      // Send the chat message
      console.log("Sending chat message..." + messageText);

      setMessages([
        ...messages,
        {
          avatarSrc: "/placeholder-user.jpg",
          avatarFallback: "OA",
          author: "Alex",
          text: messageText,
        },
      ]);

      textarea.value = "";
    }

    // Create Message component that displays the chat message in the chat window
  }

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 relative grid grid-cols-[1fr_300px]">
        <div className="relative">
          <div className="absolute inset-0 bg-muted/50 backdrop-blur-sm grid grid-cols-1 gap-2 p-4">
            <div className="rounded-xl overflow-hidden">
              <video
                className="w-full h-full object-cover"
                src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
                controls
              />
            </div>
          </div>
        </div>
        <div className="bg-background/50 backdrop-blur-sm border-l flex flex-col">
          <div className="flex-1 overflow-auto">
            <div className="p-4 space-y-4">
              {messages.map((message, index) => (
                <Message
                  key={index}
                  avatarSrc={message.avatarSrc}
                  avatarFallback={message.avatarFallback}
                  author={message.author}
                  text={message.text}
                />
              ))}
            </div>
          </div>
          <div className="bg-background/50 backdrop-blur-sm border-t flex items-center justify-center gap-4 p-4">
            <Textarea
              onKeyDown={handleKeyDown}
              ref={textareaRef}
              className="flex-1 min-h-[48px] rounded-2xl resize-none p-4 border border-neutral-400 shadow-sm"
              placeholder="Type your message..."
            />
            <Button
              onClick={sendChatMessage}
              variant="ghost"
              size="icon"
              className="text-muted-foreground"
            >
              <SendIcon className="w-6 h-6" />
            </Button>
          </div>
        </div>
      </div>
      <div className="bg-background/50 backdrop-blur-sm border-t flex items-center justify-center gap-4 p-4">
        <Button variant="ghost" size="icon" className="text-muted-foreground">
          <MicIcon className="w-6 h-6" />
        </Button>
        <Button variant="ghost" size="icon" className="text-muted-foreground">
          <VideoIcon className="w-6 h-6" />
        </Button>
        <VideoStream />
        {/* <Webcam /> */}
      </div>
    </div>
  );
}

function MicIcon(props: any) {
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
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" x2="12" y1="19" y2="22" />
    </svg>
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

function VideoIcon(props: any) {
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
      <path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5" />
      <rect x="2" y="6" width="14" height="12" rx="2" />
    </svg>
  );
}
