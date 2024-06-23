import React, { useRef, useEffect } from "react";

const VideoStream: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Initialize WebSocket connection
    socketRef.current = new WebSocket("ws://localhost:8000/ws");

    socketRef.current.onopen = () => {
      console.log("WebSocket connection established");
    };

    socketRef.current.onmessage = (event) => {
      console.log("Message from server ", event.data);
    };

    socketRef.current.onerror = (error) => {
      console.log("WebSocket error: ", error);
    };

    socketRef.current.onclose = () => {
      console.log("WebSocket connection closed");
    };

    // Access webcam
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      })
      .catch((err) => console.error("Error accessing webcam: ", err));

    // Capture and send frames
    const sendFrame = () => {
      if (canvasRef.current && videoRef.current) {
        const context = canvasRef.current.getContext("2d");
        if (context) {
          context.drawImage(
            videoRef.current,
            0,
            0,
            canvasRef.current.width,
            canvasRef.current.height
          );
          canvasRef.current.toBlob(
            (blob) => {
              if (blob && socketRef.current) {
                const reader = new FileReader();
                reader.onloadend = () => {
                  if (socketRef.current) {
                    socketRef.current.send(reader.result as string);
                  }
                };
                reader.readAsDataURL(blob);
              }
            },
            "image/jpeg"
          );
        }
      }
    };

    const interval = setInterval(sendFrame, 1000 / 30); // 30 fps

    return () => {
      clearInterval(interval);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  return (
    <div>
      <video ref={videoRef} autoPlay style={{ display: "none" }}></video>
      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        style={{ display: "none" }}
      ></canvas>
    </div>
  );
};

export default VideoStream;
