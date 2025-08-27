import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";

export default function ProyectoDetalle() {
  const { id } = useParams();
  const API = (import.meta.env && import.meta.env.VITE_API_URL) || "http://localhost:8000/api";
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`${API}/law-projects/${id}`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(setData)
      .catch(() => setData({
        name: "Ley de Transporte (mock)",
        summary: "Proyecto para mejorar la regulación del transporte público.",
        votes: { favor: 70, contra: 20, abst: 10 }
      }));
  }, [API, id]);

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4">
      <Link to="/" className="text-sm text-blue-700 hover:underline">← Volver</Link>
      <h1 className="text-2xl font-bold">{data?.name || "Proyecto"}</h1>
      <p className="text-blue-700/80">{data?.summary}</p>
      {data?.votes && (
        <div className="grid sm:grid-cols-3 gap-3">
          {[
            { label: "A favor", value: data.votes.favor + "%" },
            { label: "En contra", value: data.votes.contra + "%" },
            { label: "Abstenciones", value: data.votes.abst + "%" },
          ].map(x => (
            <div key={x.label} className="rounded-xl border border-gray-200 p-3">
              <p className="text-xs uppercase tracking-wide text-blue-700/70">{x.label}</p>
              <p className="text-2xl font-semibold">{x.value}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

