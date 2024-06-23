"use client"; // Ensure this line is at the top to mark this component as a client component

import React, { useEffect, useRef } from "react";

const Webcam: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accessing webcam: ", err);
      }
    };

    startWebcam();

    return () => {
      // Cleanup the stream
      if (videoRef.current && videoRef.current.srcObject) {
        (videoRef.current.srcObject as MediaStream)
          .getTracks()
          .forEach((track) => {
            track.stop();
          });
      }
    };
  }, []);

  return (
    <div className="webcam-container">
      <video ref={videoRef} autoPlay className="webcam-video" />
    </div>
  );
};

export default Webcam;
