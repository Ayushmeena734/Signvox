function Navbar() {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5 sm:px-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-blue-400">
            SignVox
          </h1>

          <p className="mt-1 text-xs text-slate-400 sm:text-sm">
            Bidirectional Sign Language Communication
          </p>
        </div>

        <div>
          <span className="rounded-full bg-blue-500/10 px-3 py-2 text-xs font-medium text-blue-400 sm:text-sm">
            AI Translator
          </span>
          <p className="mt-2 text-xs text-slate-400 sm:text-sm">
            Made by Ayush Meena & Atharv Deshmukh
          </p>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
