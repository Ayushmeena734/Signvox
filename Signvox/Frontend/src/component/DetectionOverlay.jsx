import React from "react";
function DetectionOverlay({ detectedSign, confidence }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">

      <p className="text-sm font-medium uppercase tracking-wider text-slate-400">
        Detected Sign
      </p>

      <div className="mt-3 flex items-center justify-between">
        <h2 className="text-3xl font-bold text-blue-400">
          {detectedSign || "Detecting..."}
        </h2>

        <span className="text-sm text-green-400">
          {detectedSign ? `${confidence}% Confidence` : "--"}
        </span>
      </div>

    </div>
  );
}

export default DetectionOverlay;