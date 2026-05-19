import { useState } from "react";
import { z } from "zod";
import { api, ErrorMessage, Severity, SeverityEnum } from "../lib/api";

const FormSchema = z.object({
  code: z.string().regex(/^0x[0-9A-F]{1,6}[A-Z]{0,2}$/, "code must match 0xHEX[ALPHA]"),
  title: z.string().min(1).max(120),
  description: z.string().min(1).max(500),
  severity: SeverityEnum,
  subsystem: z.string().min(1).max(60),
  tags: z.array(z.string()).default([]),
});

type FormState = z.infer<typeof FormSchema>;

const severities: Severity[] = ["INFO", "WARNING", "ERROR", "CRITICAL", "EXISTENTIAL"];

export default function EditModal({
  error,
  onClose,
  onSaved,
}: {
  error: ErrorMessage;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<FormState>({
    code: error.code,
    title: error.title,
    description: error.description,
    severity: error.severity,
    subsystem: error.subsystem,
    tags: error.tags || [],
  });
  const [err, setErr] = useState<string>("");
  const [saving, setSaving] = useState(false);

  const update = <K extends keyof FormState>(k: K, v: FormState[K]) =>
    setForm((f) => ({ ...f, [k]: v }));

  const regenSlot = async (slot: "title" | "description" | "code" | "subsystem") => {
    const g = await api.generate({ severity: form.severity });
    update(slot, g[slot]);
  };

  const save = async () => {
    const parsed = FormSchema.safeParse(form);
    if (!parsed.success) {
      setErr(parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; "));
      return;
    }
    setErr("");
    setSaving(true);
    try {
      await api.updateError(error.id, parsed.data);
      onSaved();
    } catch (e: any) {
      setErr(String(e?.message || e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-zinc-900 border border-white/10 rounded-lg p-6 w-[min(640px,92vw)] max-h-[90vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-xl font-bold mb-4">Edit error</h2>

        <Field label="Code" onRegen={() => regenSlot("code")}>
          <input value={form.code} onChange={(e) => update("code", e.target.value)} className="input" />
        </Field>
        <Field label="Title" onRegen={() => regenSlot("title")}>
          <input value={form.title} onChange={(e) => update("title", e.target.value)} className="input" maxLength={120} />
        </Field>
        <Field label="Description" onRegen={() => regenSlot("description")}>
          <textarea value={form.description} onChange={(e) => update("description", e.target.value)} className="input min-h-[100px]" maxLength={500} />
        </Field>
        <Field label="Severity">
          <select value={form.severity} onChange={(e) => update("severity", e.target.value as Severity)} className="input">
            {severities.map((s) => <option key={s}>{s}</option>)}
          </select>
        </Field>
        <Field label="Subsystem" onRegen={() => regenSlot("subsystem")}>
          <input value={form.subsystem} onChange={(e) => update("subsystem", e.target.value)} className="input" maxLength={60} />
        </Field>
        <Field label="Tags (comma-separated)">
          <input
            value={form.tags.join(", ")}
            onChange={(e) => update("tags", e.target.value.split(",").map((t) => t.trim()).filter(Boolean))}
            className="input"
          />
        </Field>

        {err && <p className="text-red-400 text-sm mt-2">{err}</p>}

        <div className="flex justify-end gap-3 mt-6">
          <button onClick={onClose} className="px-4 py-2 rounded bg-white/10 hover:bg-white/20">Cancel</button>
          <button onClick={save} disabled={saving} className="px-4 py-2 rounded bg-white text-black hover:bg-white/90">
            {saving ? "Saving…" : "Save"}
          </button>
        </div>

        <style>{`.input { width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 6px 10px; border-radius: 6px; color: white; }`}</style>
      </div>
    </div>
  );
}

function Field({ label, children, onRegen }: { label: string; children: React.ReactNode; onRegen?: () => void }) {
  return (
    <div className="mb-3">
      <div className="flex justify-between items-center mb-1">
        <label className="text-xs text-white/60">{label}</label>
        {onRegen && (
          <button type="button" onClick={onRegen} className="text-xs text-blue-300 hover:text-blue-200">
            ↻ regenerate
          </button>
        )}
      </div>
      {children}
    </div>
  );
}
