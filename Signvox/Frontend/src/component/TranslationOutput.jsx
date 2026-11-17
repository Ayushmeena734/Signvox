function TranslationOutput({ detectedSign, confidence }) {

  const speakText = () => {
    if (!detectedSign) return;

    const speech = new SpeechSynthesisUtterance(
      detectedSign
    );

    window.speechSynthesis.speak(speech);
  };

  return (
    <section className="flex h-full w-full flex-col rounded-2xl border border-slate-800 bg-slate-900 p-5">

      <h2 className="mb-5 text-lg font-semibold">
        Translation Output
      </h2>

      {/* Recognized Sign */}
      <div className="rounded-xl bg-slate-800 p-6">

        <p className="text-sm text-slate-400">
          Recognized Sign
        </p>

        <h3 className="mt-3 wrap-break-words text-3xl font-bold text-blue-400">
          {detectedSign || "Waiting for sign..."}
        </h3>

        <p className="mt-3 text-sm text-slate-400">
          Confidence: {detectedSign ? `${confidence}%` : "--"}
        </p>

      </div>

      {/* Voice Output */}
      <div className="mt-4 rounded-xl bg-slate-800 p-6">

        <p className="mb-3 text-sm text-slate-400">
          Voice Output
        </p>

        <p className="wrap-break-words text-xl font-medium">
          {detectedSign || " Translated speech"}
        </p>

      </div>

      <button
        onClick={speakText}
        disabled={!detectedSign}
        className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 py-3 font-medium hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
      >
        🔊 Play Audio
      </button>

    </section>
  );
}

export default TranslationOutput;