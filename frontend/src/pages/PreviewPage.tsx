import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";
import ErrorDialog from "../components/ErrorDialog";

export default function PreviewPage() {
  const { seed = "" } = useParams();
  const { data, isLoading, error } = useQuery({
    queryKey: ["preview", seed],
    queryFn: () => api.preview(seed),
    enabled: Boolean(seed),
  });

  if (isLoading) return <p className="text-center mt-12">loading…</p>;
  if (error || !data) return <p className="text-center mt-12 text-red-400">failed to load</p>;

  return (
    <div className="py-12 px-4">
      <ErrorDialog {...data} />
      <p className="text-center mt-6 text-xs text-white/50 font-mono">seed: {seed}</p>
    </div>
  );
}
