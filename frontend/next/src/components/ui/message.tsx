import React from "react";
import { Avatar, AvatarImage, AvatarFallback } from "./avatar";

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
      <Avatar className="w-8 h-8 border">
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
