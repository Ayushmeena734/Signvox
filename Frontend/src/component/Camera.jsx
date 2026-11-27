import { useEffect, useRef, useState } from "react";
import { FilesetResolver, HandLandmarker } from "@mediapipe/tasks-vision";
import { predictSign } from "../services/api";

const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],
  [0, 5], [5, 6], [6, 7], [7, 8],
  [5, 9], [9, 10], [10, 11], [11, 12],
  [9, 13], [13, 14], [14, 15], [15, 16],
  [13, 17], [17, 18], [18, 19], [19, 20],
  [0, 17],
];

function Camera({ onPrediction }) {
  const videoRef = useRef(null);
  const overlayCanvasRef = useRef(null);
  const streamRef = useRef(null);
  const landmarkerRef = useRef(null);
  const animFrameRef = useRef(null);

  const isPredictingRef = useRef(false);
  const lastPredictTimeRef = useRef(0);
  const historyRef = useRef([]);
  const isHelloActiveRef = useRef(false);

  const [cameraOn, setCameraOn] = useState(false);
  const [modelReady, setModelReady] = useState(false);
  const [error, setError] = useState("");

  // 1. Load MediaPipe HandLandmarker in Browser
  useEffect(() => {
    let active = true;

    async function initLandmarker() {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
        );
        const landmarker = await HandLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath: "/hand_landmarker.task",
            delegate: "GPU",
          },
          runningMode: "VIDEO",
          numHands: 1,
          minHandDetectionConfidence: 0.6,
          minHandPresenceConfidence: 0.6,
          minTrackingConfidence: 0.6,
        });

        if (active) {
          landmarkerRef.current = landmarker;
          setModelReady(true);
        }
      } catch (err) {
        console.error("Failed to load HandLandmarker:", err);
        if (active) setError("Hand tracking model failed to load.");
      }
    }

    initLandmarker();

    return () => {
      active = false;
      landmarkerRef.current?.close();
    };
  }, []);

  const clearOverlay = () => {
    const canvas = overlayCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  // Draw 60 FPS smooth landmarks directly on screen
  const drawLandmarks = (landmarks, isHello) => {
    const canvas = overlayCanvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;

    const width = video.clientWidth;
    const height = video.clientHeight;

    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }

    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, width, height);

    if (!landmarks || landmarks.length !== 21) return;

    ctx.strokeStyle = isHello ? "#22c55e" : "#38bdf8";
    ctx.lineWidth = 2.5;

    for (const [startIdx, endIdx] of HAND_CONNECTIONS) {
      const p1 = landmarks[startIdx];
      const p2 = landmarks[endIdx];
      ctx.beginPath();
      ctx.moveTo((1 - p1.x) * width, p1.y * height);
      ctx.lineTo((1 - p2.x) * width, p2.y * height);
      ctx.stroke();
    }

    for (let i = 0; i < landmarks.length; i++) {
      const point = landmarks[i];
      const x = (1 - point.x) * width;
      const y = point.y * height;

      ctx.beginPath();
      ctx.arc(x, y, i === 0 ? 6 : 4.5, 0, 2 * Math.PI);
      ctx.fillStyle = i === 0 ? "#facc15" : "#ef4444";
      ctx.fill();
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  };

  // Send only 63 coordinates to FastAPI backend every 150ms
  const sendLandmarksToBackend = async (rawLandmarks) => {
    const now = performance.now();
    if (isPredictingRef.current || now - lastPredictTimeRef.current < 150) {
      return;
    }

    isPredictingRef.current = true;
    lastPredictTimeRef.current = now;

    try {
      // Mirror X coordinate so it matches flipped webcam training data
      const mirroredLandmarks = rawLandmarks.map((lm) => ({
        x: 1 - lm.x,
        y: lm.y,
        z: lm.z,
      }));

      const result = await predictSign(mirroredLandmarks);

      historyRef.current.push(result.sign);
      if (historyRef.current.length > 6) {
        historyRef.current.shift();
      }

      const helloCount = historyRef.current.filter((s) => s === "HELLO").length;
      const isHello = helloCount >= 3;
      isHelloActiveRef.current = isHello;

      if (isHello) {
        onPrediction?.("HELLO", result.confidence);
      } else {
        onPrediction?.("", result.confidence);
      }
    } catch (err) {
      console.error("Prediction error:", err);
    } finally {
      isPredictingRef.current = false;
    }
  };

  // 60 FPS Rendering & Tracking Loop
  useEffect(() => {
    if (!cameraOn || !modelReady) return;

    let lastVideoTime = -1;

    const renderLoop = () => {
      const video = videoRef.current;
      const landmarker = landmarkerRef.current;

      if (video && landmarker && video.readyState >= 2) {
        if (video.currentTime !== lastVideoTime) {
          lastVideoTime = video.currentTime;
          const results = landmarker.detectForVideo(video, performance.now());

          if (results.landmarks && results.landmarks.length > 0) {
            const hand = results.landmarks[0];
            drawLandmarks(hand, isHelloActiveRef.current);
            sendLandmarksToBackend(hand);
          } else {
            clearOverlay();
            historyRef.current = [];
            isHelloActiveRef.current = false;
            onPrediction?.("", 0);
          }
        }
      }

      animFrameRef.current = requestAnimationFrame(renderLoop);
    };

    animFrameRef.current = requestAnimationFrame(renderLoop);

    return () => {
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
    };
  }, [cameraOn, modelReady, onPrediction]);

  const startCamera = async () => {
    try {
      setError("");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      historyRef.current = [];
      isHelloActiveRef.current = false;
      setCameraOn(true);
    } catch (err) {
      setError("Please allow camera access.");
      console.error(err);
    }
  };

  const stopCamera = () => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
    }

    streamRef.current?.getTracks().forEach((track) => {
      track.stop();
    });

    streamRef.current = null;
    historyRef.current = [];
    isHelloActiveRef.current = false;
    clearOverlay();
    setCameraOn(false);
    onPrediction?.("", 0);
  };

  useEffect(() => {
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Live Camera</h2>

        <span
          className={`rounded-full px-3 py-1 text-xs ${
            cameraOn
              ? "bg-green-500/10 text-green-400"
              : "bg-slate-800 text-slate-400"
          }`}
        >
          {cameraOn ? "Camera Active" : "Camera Off"}
        </span>
      </div>

      {/* Camera Preview + 60FPS Hand Landmarks Overlay */}
      <div className="relative aspect-4/3 overflow-hidden rounded-xl bg-black">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="h-full w-full -scale-x-100 object-cover"
        />

        <canvas
          ref={overlayCanvasRef}
          className="pointer-events-none absolute inset-0 h-full w-full"
        />

        {!cameraOn && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-400">
            Start camera to begin
          </div>
        )}
      </div>

      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}

      <div className="mt-5">
        {!cameraOn ? (
          <button
            onClick={startCamera}
            disabled={!modelReady}
            className="rounded-lg bg-blue-600 px-5 py-3 font-medium hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {modelReady ? "Start Camera" : "Loading Tracker..."}
          </button>
        ) : (
          <button
            onClick={stopCamera}
            className="rounded-lg bg-red-600 px-5 py-3 font-medium hover:bg-red-500"
          >
            Stop Camera
          </button>
        )}
      </div>
    </section>
  );
}

export default Camera;