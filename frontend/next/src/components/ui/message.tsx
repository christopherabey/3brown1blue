import React from "react";
import { Avatar, AvatarImage, AvatarFallback } from "./avatar";
import { cn } from "@/lib/utils";

// Define the types for the props
interface MessageProps {
  avatarSrc: string;
  avatarFallback: string;
  author: string;
  text: string;
}

const Message: React.FC<MessageProps> = ({
  avatarSrc,
  avatarFallback,
  author,
  text,
}) => {
  return (
    <div className="flex items-start gap-4">
      <Avatar
        className={cn("w-8 h-8 border-2", {
          "border-blue-800": author === "You",
          "border-orange-800": author !== "You",
        })}
      >
        <AvatarImage src={avatarSrc} />
        <AvatarFallback>{avatarFallback}</AvatarFallback>
      </Avatar>
      <div className="grid gap-1">
        <div className="font-bold">{author}</div>
        <div className="prose text-muted-foreground">
          <p>{text}</p>
        </div>
      </div>
    </div>
  );
};

export default Message;
