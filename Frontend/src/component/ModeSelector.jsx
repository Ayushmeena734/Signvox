function ModeSelector({ mode, setMode }) {
  return (
    <div className="mb-8 flex flex-wrap gap-3">

      <button
        onClick={() => setMode("sign")}
        className={`rounded-xl px-5 py-3 text-sm font-medium transition ${
          mode === "sign"
            ? "bg-blue-600 text-white"
            : "bg-slate-800 text-slate-300 hover:bg-slate-700"
        }`}
      >
        Sign → Text + Voice
      </button>

      <button
        onClick={() => setMode("text")}
        className={`rounded-xl px-5 py-3 text-sm font-medium transition ${
          mode === "text"
            ? "bg-blue-600 text-white"
            : "bg-slate-800 text-slate-300 hover:bg-slate-700"
        }`}
      >
        Voice/Text → Sign
      </button>

    </div>
  );
}

export default ModeSelector;