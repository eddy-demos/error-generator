import { Link, NavLink, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { SkinContext, Skin } from "./skin";

export default function App() {
  const [skin, setSkin] = useState<Skin>(() => (localStorage.getItem("skin") as Skin) || "win98");
  useEffect(() => { localStorage.setItem("skin", skin); }, [skin]);

  return (
    <SkinContext.Provider value={{ skin, setSkin }}>
      <div className="min-h-screen flex flex-col">
        <header className="px-6 py-4 flex items-center justify-between border-b border-white/10">
          <Link to="/" className="font-mono text-lg tracking-tight">
            <span className="text-rose-400">⚠</span> <strong>fake-error.dev</strong>
          </Link>
          <nav className="flex gap-4 text-sm">
            <NavLink to="/" end className={({ isActive }) => isActive ? "text-white" : "text-white/60 hover:text-white"}>Generator</NavLink>
            <NavLink to="/library" className={({ isActive }) => isActive ? "text-white" : "text-white/60 hover:text-white"}>Library</NavLink>
          </nav>
          <SkinTabs />
        </header>
        <main className="flex-1">
          <Outlet />
        </main>
        <footer className="px-6 py-4 text-xs text-white/40 text-center">
          generates plausible-sounding nonsense. saves it. shares it.
        </footer>
      </div>
    </SkinContext.Provider>
  );
}

function SkinTabs() {
  const skins: Skin[] = ["win98", "aqua", "terminal", "ios"];
  return (
    <SkinContext.Consumer>
      {({ skin, setSkin }) => (
        <div className="flex gap-1 text-xs">
          {skins.map((s) => (
            <button
              key={s}
              onClick={() => setSkin(s)}
              className={`px-2 py-1 rounded ${skin === s ? "bg-white text-black" : "bg-white/10 text-white/70 hover:bg-white/20"}`}
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </SkinContext.Consumer>
  );
}
