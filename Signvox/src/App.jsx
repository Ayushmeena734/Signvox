import { useState } from "react";

import Camera from "./components/Camera";
import TranslationOutput from "./components/TranslationOutput";

function App() {
  const [detectedSign, setDetectedSign] = useState("");
  const [confidence, setConfidence] = useState(0);

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 px-6 py-5">
        <h1 className="text-2xl font-bold text-blue-400">
          SignVox
        </h1>

        <p className="text-sm text-slate-400">
          Bidirectional Sign Language Communication
        </p>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-2">
        <Camera
          detectedSign={detectedSign}
          confidence={confidence}
        />

        <TranslationOutput
          detectedSign={detectedSign}
          confidence={confidence}
        />
        
      </main>
      
    </div>
  );
}

export default App;