import { useContext } from "react";
import { SkinContext } from "../skin";
import type { Severity } from "../lib/api";

export interface DialogProps {
  code: string;
  title: string;
  description: string;
  severity: Severity;
  subsystem: string;
}

function SeverityIcon({ severity }: { severity: Severity }) {
  const map: Record<Severity, string> = {
    INFO: "ℹ",
    WARNING: "⚠",
    ERROR: "✕",
    CRITICAL: "☠",
    EXISTENTIAL: "∞",
  };
  return <span className={`sev-${severity}`} aria-hidden>{map[severity]}</span>;
}

export default function ErrorDialog({ code, title, description, severity, subsystem }: DialogProps) {
  const { skin } = useContext(SkinContext);

  const titleBar = (
    <div className="title-bar">
      <span className="flex items-center gap-2">
        <SeverityIcon severity={severity} />
        <span>{code}</span>
      </span>
      <span className="opacity-70 text-xs">{subsystem}</span>
    </div>
  );

  return (
    <div className={`skin-${skin} w-[min(560px,92vw)] mx-auto`}>
      {skin === "aqua" ? (
        <div className="title-bar">
          <span className="traffic red" />
          <span className="traffic yellow" />
          <span className="traffic green" />
          <span className="ml-2 text-sm font-medium">{code} — {subsystem}</span>
        </div>
      ) : (
        titleBar
      )}
      <div className="body">
        <div className="flex items-start gap-4">
          <div className="text-4xl"><SeverityIcon severity={severity} /></div>
          <div className="flex-1">
            <h2 className={`text-xl font-bold mb-2 sev-${severity}`}>{title}</h2>
            <p className="opacity-90 leading-relaxed">{description}</p>
            <div className="mt-3 text-xs opacity-60">
              <span className={`badge sev-${severity}`}>{severity}</span>
            </div>
          </div>
        </div>
        <div className="mt-6 flex gap-2 justify-end">
          <button className="btn" type="button">OK</button>
          <button className="btn" type="button">Pretend to Restart</button>
        </div>
      </div>
    </div>
  );
}
