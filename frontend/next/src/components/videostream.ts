import React, { useRef, useEffect } from "react";

const VideoStream = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const socketRef = useRef(null);

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
        videoRef.current.srcObject = stream;
      })
      .catch((err) => console.error("Error accessing webcam: ", err));

    // Capture and send frames
    const sendFrame = () => {
      const context = canvasRef.current.getContext("2d");
      context.drawImage(
        videoRef.current,
        0,
        0,
        canvasRef.current.width,
        canvasRef.current.height
      );
      canvasRef.current.toBlob((blob) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          socketRef.current.send(reader.result);
        };
        reader.readAsDataURL(blob);
      }, "image/jpeg");
    };

    const interval = setInterval(sendFrame, 1000 / 30); // 30 fps

    return () => {
      clearInterval(interval);
      socketRef.current.close();
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
