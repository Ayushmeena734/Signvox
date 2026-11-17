import { useEffect, useRef, useState } from "react";

function Camera() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const [cameraOn, setCameraOn] = useState(false);
  const [error, setError] = useState("");

  const startCamera = async () => {
    try {
      setError("");

      const stream =
        await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      setCameraOn(true);

    } catch (err) {
      setError("Please allow camera access.");
      console.error(err);
    }
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach((track) => {
      track.stop();
    });

    streamRef.current = null;
    setCameraOn(false);
  };

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => {
        track.stop();
      });
    };
  }, []);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5">

      <div className="mb-4 flex items-center justify-between">

        <h2 className="text-lg font-semibold">
          Live Camera
        </h2>

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

      {/* Camera Preview */}
<div className="relative aspect-4/3 overflow-hidden rounded-xl bg-black">
    <video
    ref={videoRef}
    autoPlay
    playsInline
    muted
    className="h-full w-full object-cover"
  />

  {!cameraOn && (
    <div className="absolute inset-0 flex items-center justify-center text-slate-400">
      Start camera to begin
    </div>
  )}
</div>

      {error && (
        <p className="mt-3 text-sm text-red-400">
          {error}
        </p>
      )}

      <div className="mt-5">

        {!cameraOn ? (
          <button
            onClick={startCamera}
            className="rounded-lg bg-blue-600 px-5 py-3 font-medium hover:bg-blue-500"
          >
            Start Camera
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