import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";

export default function ParlamentarioDetalle() {
  const { id } = useParams();
  const API = (import.meta.env && import.meta.env.VITE_API_URL) || "http://localhost:8000/api";
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`${API}/parliament-members/${id}`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(setData)
      .catch(() => setData({
        name: "Diputado Juan Pérez (mock)",
        party: "Independiente",
        district: "Santiago Centro",
        last_votes: [
          { project: "Reforma a la Educación", vote: "A favor" },
          { project: "Ley de Transporte", vote: "En contra" },
        ],
      }));
  }, [API, id]);

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4">
      <Link to="/" className="text-sm text-blue-700 hover:underline">← Volver</Link>
      <h1 className="text-2xl font-bold">{data?.name || "Parlamentario"}</h1>
      <p className="text-blue-700/80">
        Partido: {data?.party} • Distrito: {data?.district}
      </p>
      <div className="mt-4">
        <p className="text-sm font-semibold mb-2">Últimas votaciones</p>
        <ul className="space-y-1 text-sm">
          {(data?.last_votes || []).map((v, i) => (
            <li key={i} className="flex items-center justify-between rounded-lg border border-gray-200 px-3 py-2">
              <span>{v.project}</span>
              <span>{v.vote}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
