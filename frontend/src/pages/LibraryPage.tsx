import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ErrorMessage, Severity } from "../lib/api";
import EditModal from "../components/EditModal";

const severities: (Severity | "")[] = ["", "INFO", "WARNING", "ERROR", "CRITICAL", "EXISTENTIAL"];

export default function LibraryPage() {
  const qc = useQueryClient();
  const [severity, setSeverity] = useState<Severity | "">("");
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [q, setQ] = useState("");
  const [tag, setTag] = useState("");
  const [page, setPage] = useState(1);
  const [editing, setEditing] = useState<ErrorMessage | null>(null);

  const params = {
    severity: severity || undefined,
    favorite: favoritesOnly || undefined,
    q: q || undefined,
    tag: tag || undefined,
    page,
    limit: 20,
  };

  const { data, isLoading } = useQuery({
    queryKey: ["errors", params],
    queryFn: () => api.listErrors(params),
  });

  const toggleFav = useMutation({
    mutationFn: (e: ErrorMessage) => api.updateError(e.id, { is_favorite: !e.is_favorite }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["errors"] }),
  });

  const del = useMutation({
    mutationFn: (id: string) => api.deleteError(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["errors"] }),
  });

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.limit)) : 1;

  return (
    <div className="px-6 py-8 grid md:grid-cols-[220px_1fr] gap-8 max-w-6xl mx-auto">
      <aside className="space-y-4 text-sm">
        <div>
          <label className="block text-xs text-white/60 mb-1">Severity</label>
          <select value={severity} onChange={(e) => { setSeverity(e.target.value as Severity | ""); setPage(1); }} className="w-full bg-white/10 rounded px-2 py-1">
            {severities.map((s) => <option key={s || "any"} value={s}>{s || "any"}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs text-white/60 mb-1">Search</label>
          <input value={q} onChange={(e) => { setQ(e.target.value); setPage(1); }} className="w-full bg-white/10 rounded px-2 py-1" placeholder="title/description" />
        </div>
        <div>
          <label className="block text-xs text-white/60 mb-1">Tag</label>
          <input value={tag} onChange={(e) => { setTag(e.target.value); setPage(1); }} className="w-full bg-white/10 rounded px-2 py-1" placeholder="e.g. cursed" />
        </div>
        <label className="flex gap-2 items-center">
          <input type="checkbox" checked={favoritesOnly} onChange={(e) => { setFavoritesOnly(e.target.checked); setPage(1); }} />
          favorites only
        </label>
      </aside>

      <section>
        <h1 className="text-2xl font-bold mb-4">Library {data && <span className="text-white/40 text-sm">({data.total})</span>}</h1>
        {isLoading && <p>loading…</p>}
        {data && data.items.length === 0 && <p className="text-white/50">no errors saved yet — go generate some.</p>}
        <ul className="grid sm:grid-cols-2 gap-3">
          {data?.items.map((e) => (
            <li key={e.id} className="bg-white/5 hover:bg-white/10 rounded-lg p-4 border border-white/10">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-mono text-xs text-white/50">{e.code}</p>
                  <h3 className={`font-semibold sev-${e.severity}`}>{e.title}</h3>
                </div>
                <span className={`badge sev-${e.severity}`}>{e.severity}</span>
              </div>
              <p className="text-sm text-white/70 mt-2 line-clamp-3">{e.description}</p>
              <div className="mt-3 text-xs text-white/40 flex justify-between items-center">
                <span>{e.subsystem} · {new Date(e.created_at).toLocaleDateString()}</span>
                <div className="flex gap-2">
                  <button onClick={() => toggleFav.mutate(e)} title="favorite" className="hover:text-yellow-400">
                    {e.is_favorite ? "★" : "☆"}
                  </button>
                  <button onClick={() => setEditing(e)} className="hover:text-white">edit</button>
                  <button
                    onClick={() => { if (confirm("delete this error?")) del.mutate(e.id); }}
                    className="hover:text-red-400"
                  >
                    del
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>

        {data && data.total > data.limit && (
          <div className="flex justify-center gap-3 mt-6 text-sm">
            <button disabled={page === 1} onClick={() => setPage(page - 1)} className="px-3 py-1 bg-white/10 rounded disabled:opacity-30">prev</button>
            <span className="text-white/60">page {page} / {totalPages}</span>
            <button disabled={page >= totalPages} onClick={() => setPage(page + 1)} className="px-3 py-1 bg-white/10 rounded disabled:opacity-30">next</button>
          </div>
        )}
      </section>

      {editing && (
        <EditModal
          error={editing}
          onClose={() => setEditing(null)}
          onSaved={() => { setEditing(null); qc.invalidateQueries({ queryKey: ["errors"] }); }}
        />
      )}
    </div>
  );
}
