"use client";

import { cn } from "@/lib/utils";
import { useState } from "react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { SendIcon } from "lucide-react";

export default function StartingComponent() {
  const [starting, setStarting] = useState(true);

  const handleButtonClick = () => {};

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {};
  return (
    <div className="w-full h-full flex relative items-center align-middle justify-center">
      <div
        className={cn("flex flex-col w-[80%] gap-4", {
          "absolute top-1/3 left-1/2 transform -translate-x-1/2 -translate-y-1/2":
            starting,
          "bottom-8 left-auto right-auto": !starting,
        })}
      >
        {starting && (
          <>
            <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center">
              Welcome to <span className=" text-orange-800">3 Brown</span>{" "}
              <span className="text-blue-800">1 Blue</span>
            </h1>
            <h2 className="text-lg text-center text-muted-foreground">
              Enter a topic to learn more about it
            </h2>
          </>
        )}

        <div className="flex flex-row gap-2 items-center align-middle justify-center mt-8">
          <Input
            type="text"
            className={cn(
              "w-full h-12 px-4 py-2 border border-gray-300 rounded-md  shadow-md text-xl text-foreground font-semibold"
            )}
            placeholder="Let's learn!"
          />
          <Button
            onClick={handleButtonClick}
            variant="ghost"
            size="icon"
            className="text-muted-foreground"
            style={{
              transform: "translateX(-55px)",
            }}
          >
            <SendIcon className="w-6 h-6" />
          </Button>
        </div>
      </div>
    </div>
  );
}
