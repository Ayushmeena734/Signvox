import { useState, useEffect, useCallback } from "react";

import { testBackend } from "./services/api";
import Navbar from "./component/Navbar";
import ModeSelector from "./component/ModeSelector";
import Camera from "./component/Camera";
import DetectionOverlay from "./component/DetectionOverlay";
import TranslationOutput from "./component/TranslationOutput";
import TextToSign from "./component/TextToSign";

function App() {
  const [mode, setMode] = useState("sign");

  const [detectedSign, setDetectedSign] = useState("");
  const [confidence, setConfidence] = useState(0);

  const [backendStatus, setBackendStatus] = useState("Connecting...");

  const handlePrediction = useCallback((sign, conf) => {
    setDetectedSign(sign);
    setConfidence(conf);
  }, []);

  // Backend connection check
  useEffect(() => {
    testBackend()
      .then((data) => {
        setBackendStatus(data.status);
        console.log(data);
      })
      .catch((error) => {
        setBackendStatus("Connection failed");
        console.error(error);
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Navbar />

      <p className="text-center text-green-400">Backend: {backendStatus}</p>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <ModeSelector mode={mode} setMode={setMode} />

        {mode === "sign" ? (
          <div className="grid grid-cols-1 items-stretch gap-5 lg:grid-cols-5">
            {/* Camera + Detected Sign */}
            <div className="flex flex-col gap-5 lg:col-span-3">
              <Camera onPrediction={handlePrediction} />

              <DetectionOverlay
                detectedSign={detectedSign}
                confidence={confidence}
              />
            </div>

            {/* Translation Output */}
            <div className="flex lg:col-span-2">
              <TranslationOutput
                detectedSign={detectedSign}
                confidence={confidence}
              />
            </div>
          </div>
        ) : (
          <TextToSign />
        )}
      </main>

      <footer className="border-t border-slate-800 py-5 text-center text-sm text-slate-500">
        SignVox • Bidirectional Sign Language Communication
      </footer>
    </div>
  );
}

export default App;