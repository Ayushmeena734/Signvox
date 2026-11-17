import { useState } from "react";

function TextToSign() {
  const [textInput, setTextInput] = useState("");
  const [signOutput, setSignOutput] = useState("");

  const translateText = () => {
    if (!textInput.trim()) return;

    setSignOutput(textInput.trim());
  };

  const reset = () => {
    setTextInput("");
    setSignOutput("");
  };

  return (
    <section className="mx-auto max-w-3xl rounded-2xl border border-slate-800 bg-slate-900 p-6">

      <h2 className="text-xl font-semibold">
        Voice/Text to Sign
      </h2>

      <p className="mt-2 text-sm text-slate-400">
        Enter a word or phrase to find its matching sign.
      </p>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">

        <input
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          placeholder="Enter a word, e.g. Hello"
          className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 outline-none focus:border-blue-500"
        />

        <button
          onClick={translateText}
          className="rounded-lg bg-blue-600 px-6 py-3 font-medium hover:bg-blue-500"
        >
          Find Sign
        </button>

      </div>

      <div className="mt-6 flex min-h-64 flex-col items-center justify-center rounded-xl bg-slate-800 p-6 text-center">

        {signOutput ? (
          <>
            <div className="mb-4 text-6xl">
              🤟
            </div>

            <h3 className="text-2xl font-bold text-blue-400">
              {signOutput}
            </h3>

            <p className="mt-2 text-sm text-slate-400">
              Matching sign reference
            </p>
          </>
        ) : (
          <p className="text-slate-400">
             Sign reference will appear here.
          </p>
        )}

      </div>

      <button
        onClick={reset}
        className="mt-5 rounded-lg bg-slate-800 px-5 py-3 hover:bg-slate-700"
      >
        Reset
      </button>

    </section>
  );
}

export default TextToSign;