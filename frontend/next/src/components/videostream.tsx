import React, { useEffect, useRef, useState } from 'react';

const VideoStream: React.FC = () => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [isSocketOpen, setIsSocketOpen] = useState<boolean>(false);
    const [messages, setMessages] = useState<string[]>([]);
    
    useEffect(() => {
        // Open WebSocket connection
        const ws = new WebSocket('ws://localhost:8000/ws');
        
        ws.onopen = () => {
            setIsSocketOpen(true);
            setSocket(ws);
        };

        ws.onmessage = (event) => {
            const result = JSON.parse(event.data);
            setMessages((prevMessages) => [...prevMessages, JSON.stringify(result)]);
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

    useEffect(() => {
        if (videoRef.current) {
            const video = videoRef.current;
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    video.srcObject = stream;
                    video.play();
                })
                .catch(error => {
                    console.error("Error accessing webcam:", error);
                });
        }
    }, []);

    useEffect(() => {
        const captureFrame = () => {
            if (videoRef.current && socket && isSocketOpen) {
                const canvas = document.createElement('canvas');
                canvas.width = videoRef.current.videoWidth;
                canvas.height = videoRef.current.videoHeight;
                const context = canvas.getContext('2d');
                context?.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

                const frameData = canvas.toDataURL('image/png');
                socket.send(frameData);

                setTimeout(captureFrame, 100); // Adjust interval as needed
            } else {
                setTimeout(captureFrame, 100); // Retry after a delay
            }
        };

        captureFrame();
    }, [socket, isSocketOpen]);

    return (
        <div>
            <h1>Video Stream</h1>
            <video ref={videoRef} style={{ width: '100%' }}></video>
            <div>
                <h2>Messages:</h2>
                <ul>
                    {messages.map((msg, index) => (
                        <li key={index}>{msg}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default VideoStream;
