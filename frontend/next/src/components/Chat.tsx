import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import React, { useState, useRef, RefObject, useEffect } from "react";
import { VoiceProvider } from "@humeai/voice-react";
import { useVoice } from "@humeai/voice-react";
import Messages from "./Messages";
import Message from "@/components/ui/message";
import Controls from "./Controls";

interface Message {
  avatarSrc: string;
  avatarFallback: string;
  author: string;
  text: string;
  side: "user" | "receiver";
}

export function Chat({ accessToken }: { accessToken: string }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef: RefObject<HTMLTextAreaElement> = useRef(null);
  const [messages, setMessages] = useState<Message[]>([]);

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <VoiceProvider auth={{ type: "accessToken", value: accessToken }}>
      <Controls />
      <div className="bg-background/50 backdrop-blur-sm border-l flex flex-col overflow-hidden">
        <div ref={scrollRef} className="flex-1 overflow-scroll">
          <Messages />
        </div>
      </div>
    </VoiceProvider>
  );
}
