"use client";

import React, { useState, useRef, RefObject, useEffect, useMemo } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import VideoStream from "@/components/videostream"; // Adjust the path as per your file structure
import { Progress } from "./ui/progress";
import { LoadingSpinner } from "./ui/LoadingSpinner";
import { useTheme } from "next-themes";
import { cn } from "@/lib/utils";
import { Input } from "./ui/input";
import { ChevronDown, PlayIcon, SendIcon } from "lucide-react";
import { Chat } from "./Chat";
import { useVoice } from "@humeai/voice-react";

interface Message {
  avatarSrc: string;
  avatarFallback: string;
  author: string;
  text: string;
  side: "user" | "receiver";
}

export function ClientComponent({ accessToken }: { accessToken: string }) {
  const textareaRef: RefObject<HTMLInputElement> = useRef(null);
  const [videoID, setVideoID] = useState<string>("");
  const [emotions, setEmotions] = useState<string>(""); // string of comma-separated emotions
  const [videoPlaying, setVideoPlaying] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [starting, setStarting] = useState<boolean>(true);
  const [showGame, setShowGame] = useState<boolean>(false);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isSocketOpen, setIsSocketOpen] = useState<boolean>(false);

  useEffect(() => {
    // Open WebSocket connection
    console.log("Opening WebSocket connection...");
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      setIsSocketOpen(true);
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const result = JSON.parse(event.data);

      if (result?.face?.predictions) {
        setEmotions(
          result.face.predictions[0]?.emotions
            ?.sort((a: any, b: any) => b.score - a.score)
            .slice(0, 3)
            .map((emotion: any) => emotion.name)
            .join(", ")
        );
      } else {
        setEmotions("");
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed");
      setIsSocketOpen(false);
    };

    return () => {
      ws.close();
    };
  }, []);

  function generateVideo() {
    setStarting(false);
    setVideoPlaying(false);
    setVideoID("");
    const textarea = textareaRef.current;

    if (textarea) {
      const messageText = textarea.value;

      if (messageText.trim() === "") {
        return;
      }

      // Send the chat message
      console.log("Sending chat message..." + messageText);

      textarea.value = "";

      setLoading(true);
      // setTheme("dark");

      // Make a fetch request to the backend
      fetch("http://localhost:8000/generate_stub/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: messageText, emotions: emotions }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json(); // or .text() or .blob() depending on your response type
        })
        .then((data) => {
          // Handle the data received from the backend
          console.log(data);
          setVideoID(data.video_id);
        })
        .catch((error) => {
          // Handle errors
          console.error("Fetch error:", error);
          setLoading(false);
        });
    }
  }

  const startPlayingVideo = () => {
    setVideoPlaying(true);
    setLoading(false);
  };

  const LoadingComponent = () => {
    console.log("rendering loading component");
    return (
      <div className="w-full h-full flex flex-col p-4 gap-4 overflow-hidden">
        <div className="flex flex-col gap-4 items-center justify-center">
          {videoID ? (
            <Button onClick={startPlayingVideo} variant="outline">
              <VideoIcon className="w-6 h-6 mr-2" />
              Watch the explainer video
            </Button>
          ) : (
            <h2 className="text-4xl font-bold text-center text-gray-800 flex flex-row items-center justify-center gap-4">
              <LoadingSpinner />
              {" Generating video. This might take a while..."}
            </h2>
          )}
          <h3 className="text-2xl font-semibold text-center text-orange-600 flex flex-row items-center justify-center gap-4">
            In the meantime, how's your day going?
          </h3>
        </div>
        <div className="w-full flex justify-center align-middle items-center flex-col">
          <div className="w-full flex flex-row max-h-full overflow-scroll">
            <Chat accessToken={accessToken} />
            <VideoStream
              socket={socket}
              emotions={emotions}
              isSocketOpen={isSocketOpen}
            />
          </div>

          <Button
            onClick={() => setShowGame((prev) => !prev)}
            variant="outline"
          >
            {showGame ? (
              <ChevronDown className="w-4 h-4 mr-2" />
            ) : (
              <PlayIcon className="w-4 h-4 mr-2" />
            )}
            Or play a game
          </Button>
          {showGame && (
            <div className="animate-fade-in w-full">
              <iframe src="dinosaur_game.html" className="w-full h-80 my-8" />
            </div>
          )}
        </div>
      </div>
    );
  };

  const StartingComponent = () => {
    return (
      <div className="w-full h-full flex relative items-center align-middle justify-center">
        {videoPlaying && videoID && (
          <div className="w-full h-full flex flex-col items-center justify-center object-cover">
            <video
              src={`http://localhost:8000/videos/${videoID}/`}
              className="w-full h-full"
              controls
              autoPlay
            />
          </div>
        )}

        <div
          className={cn(
            "flex flex-col w-[80%] absolute  gap-4 transition-all ease-in-out h-full py-12",
            {
              "top-1/3 left-1/2 transform -translate-x-1/2": starting,
              "bottom-8 left-auto right-auto": !starting,
            }
          )}
        >
          {starting && (
            <>
              <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-center">
                Welcome to <span className="text-orange-800">3Brown</span>
                <span className="text-blue-800">1Blue</span>
              </h1>
              <h2 className="text-lg text-center text-muted-foreground">
                Enter a topic to learn more about it
              </h2>
            </>
          )}

          {loading && <LoadingComponent />}

          <div className="flex flex-row gap-2 items-center align-middle justify-center mt-8">
            <Input
              disabled={loading}
              ref={textareaRef}
              type="text"
              className={cn(
                "w-full h-12 px-4 py-2 border border-gray-300 rounded-md  shadow-md text-xl text-foreground font-semibold"
              )}
              placeholder="Let's learn!"
              onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  generateVideo();
                }
              }}
            />
            <Button
              onClick={generateVideo}
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
  };

  return StartingComponent();
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
