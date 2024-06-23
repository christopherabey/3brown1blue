import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import React, { useState, useRef, RefObject, useEffect } from "react";
import { VoiceProvider } from "@humeai/voice-react";
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

      setMessages((prevMessages) => [
        ...prevMessages,
        {
          avatarSrc: "/placeholder-user.jpg",
          avatarFallback: "OA",
          author: "You",
          text: messageText,
          side: "user",
        },
      ]);

      textarea.value = "";
    }
  }

  return (
    <VoiceProvider auth={{ type: "accessToken", value: accessToken }}>
      <Messages />
      <Controls />
      <div className="bg-background/50 backdrop-blur-sm border-l flex flex-col overflow-hidden">
        <div ref={scrollRef} className="flex-1 overflow-scroll">
          <div className="p-4 space-y-4 overflow-y-auto">
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
    </VoiceProvider>
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
