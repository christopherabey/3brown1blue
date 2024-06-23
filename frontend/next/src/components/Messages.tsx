// ./components/Messages.tsx
"use client";
import { useVoice } from "@humeai/voice-react";
import Message from "@/components/ui/message";

export default function Messages() {
  const { messages } = useVoice();

  return (
    <div className="p-4 space-y-4 overflow-y-auto">
      {messages.map((msg, index) => {
        if (msg.type === "user_message" || msg.type === "assistant_message") {
          return (
            <Message
              key={index}
              avatarSrc="/placeholder-user.jpg"
              avatarFallback="OA"
              author={msg.message.role}
              text={msg.message.content}
            />
          );
        }

        return null;
      })}
    </div>
  );
}
