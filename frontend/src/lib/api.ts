import { z } from "zod";

const API_BASE = "/api";

export const SeverityEnum = z.enum([
  "INFO",
  "WARNING",
  "ERROR",
  "CRITICAL",
  "EXISTENTIAL",
]);
export type Severity = z.infer<typeof SeverityEnum>;

export const ErrorSchema = z.object({
  id: z.string(),
  code: z.string(),
  title: z.string(),
  description: z.string(),
  severity: SeverityEnum,
  subsystem: z.string(),
  tags: z.array(z.string()).default([]),
  is_favorite: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type ErrorMessage = z.infer<typeof ErrorSchema>;

export const GeneratedSchema = z.object({
  code: z.string(),
  title: z.string(),
  description: z.string(),
  severity: SeverityEnum,
  subsystem: z.string(),
  tags: z.array(z.string()).default([]),
  seed: z.string(),
});
export type Generated = z.infer<typeof GeneratedSchema>;

export const ErrorListSchema = z.object({
  items: z.array(ErrorSchema),
  total: z.number(),
  page: z.number(),
  limit: z.number(),
});
export type ErrorList = z.infer<typeof ErrorListSchema>;

async function request<T>(path: string, init?: RequestInit, parser?: (j: unknown) => T): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as unknown as T;
  const json = await res.json();
  return parser ? parser(json) : (json as T);
}

export const api = {
  generate: (body: { severity?: Severity; subsystem?: string; seed?: string } = {}) =>
    request("/generate", { method: "POST", body: JSON.stringify(body) }, (j) => GeneratedSchema.parse(j)),

  preview: (seed: string) =>
    request(`/preview/${encodeURIComponent(seed)}`, {}, (j) => GeneratedSchema.parse(j)),

  listErrors: (params: Record<string, string | number | boolean | undefined> = {}) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "" && v !== null) qs.set(k, String(v));
    });
    return request(`/errors?${qs.toString()}`, {}, (j) => ErrorListSchema.parse(j));
  },

  getError: (id: string) =>
    request(`/errors/${id}`, {}, (j) => ErrorSchema.parse(j)),

  createError: (body: Omit<ErrorMessage, "id" | "created_at" | "updated_at">) =>
    request("/errors", { method: "POST", body: JSON.stringify(body) }, (j) => ErrorSchema.parse(j)),

  updateError: (id: string, body: Partial<ErrorMessage>) =>
    request(`/errors/${id}`, { method: "PATCH", body: JSON.stringify(body) }, (j) => ErrorSchema.parse(j)),

  deleteError: (id: string) =>
    request(`/errors/${id}`, { method: "DELETE" }),

  stats: () => request<{ total: number; favorites: number; by_severity: Record<string, number>; top_subsystems: { subsystem: string; count: number }[] }>("/stats"),
};
