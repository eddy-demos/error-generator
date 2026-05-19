import { useEffect, useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { toPng } from "html-to-image";

import { api, Severity, Generated } from "../lib/api";
import ErrorDialog from "../components/ErrorDialog";

const severities: (Severity | "")[] = ["", "INFO", "WARNING", "ERROR", "CRITICAL", "EXISTENTIAL"];

export default function HomePage() {
  const [current, setCurrent] = useState<Generated | null>(null);
  const [severity, setSeverity] = useState<Severity | "">("");
  const [subsystem, setSubsystem] = useState<string>("");
  const [savedMsg, setSavedMsg] = useState<string>("");
  const dialogRef = useRef<HTMLDivElement>(null);

  const generate = useMutation({
    mutationFn: () =>
      api.generate({
        severity: severity || undefined,
        subsystem: subsystem || undefined,
      }),
    onSuccess: (data) => setCurrent(data),
  });

  const save = useMutation({
    mutationFn: () => {
      if (!current) throw new Error("nothing to save");
      return api.createError({
        code: current.code,
        title: current.title,
        description: current.description,
        severity: current.severity,
        subsystem: current.subsystem,
        tags: current.tags,
        is_favorite: false,
      });
    },
    onSuccess: () => {
      setSavedMsg("Saved to library");
      setTimeout(() => setSavedMsg(""), 2000);
    },
  });

  useEffect(() => {
    if (!current) generate.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const copyText = async () => {
    if (!current) return;
    await navigator.clipboard.writeText(
      `${current.code} — ${current.title}\n${current.description}\n[${current.severity}/${current.subsystem}]`
    );
    setSavedMsg("Copied text");
    setTimeout(() => setSavedMsg(""), 1500);
  };

  const copyImage = async () => {
    if (!dialogRef.current) return;
    const dataUrl = await toPng(dialogRef.current, { cacheBust: true });
    // Try Clipboard API w/ image; fall back to download
    try {
      const blob = await (await fetch(dataUrl)).blob();
      // @ts-ignore
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
      setSavedMsg("Copied image");
    } catch {
      const a = document.createElement("a");
      a.href = dataUrl;
      a.download = `${current?.code || "error"}.png`;
      a.click();
      setSavedMsg("Downloaded image");
    }
    setTimeout(() => setSavedMsg(""), 1500);
  };

  const share = async () => {
    if (!current) return;
    const url = `${window.location.origin}/preview/${current.seed}`;
    await navigator.clipboard.writeText(url);
    setSavedMsg("Share URL copied");
    setTimeout(() => setSavedMsg(""), 1500);
  };

  return (
    <div className="py-10 px-4">
      <div className="max-w-3xl mx-auto flex flex-wrap items-center gap-2 mb-6 justify-center">
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value as Severity | "")}
          className="bg-white/10 px-3 py-1 rounded text-sm"
        >
          {severities.map((s) => (
            <option key={s || "any"} value={s}>{s || "any severity"}</option>
          ))}
        </select>
        <input
          placeholder="subsystem (optional)"
          value={subsystem}
          onChange={(e) => setSubsystem(e.target.value)}
          className="bg-white/10 px-3 py-1 rounded text-sm"
        />
        {current && (
          <span className="text-xs text-white/50 font-mono ml-auto">seed: {current.seed}</span>
        )}
      </div>

      <div ref={dialogRef}>
        {current && <ErrorDialog {...current} />}
      </div>

      <div className="mt-8 flex flex-wrap gap-3 justify-center">
        <button
          onClick={() => generate.mutate()}
          disabled={generate.isPending}
          className="bg-white text-black px-5 py-2 rounded font-semibold hover:bg-white/90"
        >
          {generate.isPending ? "Generating…" : "Generate Another"}
        </button>
        <button onClick={() => save.mutate()} className="bg-white/10 px-4 py-2 rounded hover:bg-white/20">Save</button>
        <button onClick={copyText} className="bg-white/10 px-4 py-2 rounded hover:bg-white/20">Copy as text</button>
        <button onClick={copyImage} className="bg-white/10 px-4 py-2 rounded hover:bg-white/20">Copy as image</button>
        <button onClick={share} className="bg-white/10 px-4 py-2 rounded hover:bg-white/20">Share</button>
      </div>

      {savedMsg && <p className="text-center mt-4 text-emerald-400 text-sm">{savedMsg}</p>}
    </div>
  );
}
