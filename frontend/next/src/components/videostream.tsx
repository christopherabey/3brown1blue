import React, { useEffect, useRef, useState } from "react";

interface VideoStreamProps {
  emotions: string;
  socket: WebSocket | null;
  isSocketOpen: boolean;
}

const VideoStream: React.FC<VideoStreamProps> = ({
  emotions,
  socket,
  isSocketOpen,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play();
            videoRef.current.style.transform = "scaleX(-1)"; // Mirror effect
          }
        })
        .catch((error) => {
          console.error("Error accessing webcam:", error);
        });
    }
  }, []);

  useEffect(() => {
    const captureFrame = () => {
      if (videoRef.current && socket && isSocketOpen) {
        const canvas = document.createElement("canvas");
        canvas.width = 300; // Use width and height props directly
        canvas.height = 200;
        const context = canvas.getContext("2d");
        if (context) {
          context.drawImage(
            videoRef.current,
            0,
            0,
            canvas.width,
            canvas.height
          );
          const frameData = canvas.toDataURL("image/png");
          socket.send(frameData);
        }

        setTimeout(captureFrame, 1000); // Adjust interval as needed
      } else {
        setTimeout(captureFrame, 1000); // Retry after a delay
      }
    };

    captureFrame();
  }, [socket, isSocketOpen]); // Include width and height in dependencies

  return (
    <div>
      <p
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          color: "white",
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          padding: "5px",
          margin: "0",
        }}
      >
        {emotions}
      </p>
      <video
        className="rounded-br-lg rounded-tl-lg"
        ref={videoRef}
        width={300}
        height={200}
        style={{ transform: "scaleX(-1)" }}
      ></video>
    </div>
  );
};

export default VideoStream;
