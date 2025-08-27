import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function Card({ title, children, className = "" }) {
  return (
    <section
      className={`bg-white rounded-2xl shadow-sm border border-gray-200 p-5 ${className}`}
      aria-label={title || undefined}
    >
      {title && <h2 className="text-lg font-semibold tracking-tight mb-3">{title}</h2>}
      {children}
    </section>
  );
}

function Pill({ children }) {
  return (
    <span className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
      {children}
    </span>
  );
}

function QueSeVotoHoy() {
  const API =
    (import.meta.env && import.meta.env.VITE_API_URL) ||
    "http://localhost:8000/api";

  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("idle"); // idle | loading | error | ok

  useEffect(() => {
    setStatus("loading");
    fetch(`${API}/law-projects?voted=today&limit=9`)
      .then((r) => {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then((data) => {
        setItems(data?.items ?? []);
        setStatus("ok");
      })
      .catch(() => {
        // fallback a mock cuando no hay API
        setItems([
          { id: "m1", titulo: "Reforma a la Educación", estado: "En discusión" },
          { id: "m2", titulo: "Ley de Transporte", estado: "Aprobado" },
          { id: "m3", titulo: "Seguridad Pública", estado: "Rechazado" },
        ]);
        setStatus("error");
      });
  }, [API]);

  if (status === "loading") {
    return (
      <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <li key={i} className="rounded-xl border border-gray-200 p-4 animate-pulse">
            <div className="h-4 w-3/4 bg-gray-200 rounded mb-3" />
            <div className="h-6 w-20 bg-gray-200 rounded" />
          </li>
        ))}
      </ul>
    );
  }

  return (
    <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map((p, i) => (
        <li key={p.id || i} className="rounded-xl border border-gray-200 p-4 hover:shadow-sm transition">
          <div className="flex items-start justify-between gap-3">
            <p className="font-medium leading-tight">
              {p.titulo || p.name || p.project_name}
            </p>
            <Pill>{p.estado || p.status || "—"}</Pill>
          </div>
          <Link
            to={`/proyectos/${p.id || i}`}
            className="mt-3 text-sm font-medium text-blue-700 hover:underline"
          >
            Ver detalle →
          </Link>
        </li>
      ))}
    </ul>
  );
}

export default function WireframeLegislativo() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/90 backdrop-blur border-b border-gray-200">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-blue-600" aria-hidden />
          <h1 className="text-xl font-semibold">Capisci</h1>
          <div className="ml-auto">
            <label className="sr-only" htmlFor="search">Buscar</label>
            <input
              id="search"
              type="search"
              placeholder="Buscar proyecto o parlamentario…"
              className="w-72 md:w-96 rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-200"
            />
          </div>
        </div>
      </header>

      {/* Contenido */}
      <main className="mx-auto max-w-6xl px-4 py-6 space-y-6">
        {/* Qué se votó hoy (dinámico/fallback mock) */}
        <Card title="Qué se votó hoy">
          <QueSeVotoHoy />
        </Card>

        {/* Detalle de proyecto (mock) */}
        <Card title="Detalle de proyecto">
          <div className="space-y-2">
            <p className="text-base font-medium">Ley de Transporte</p>
            <p className="text-sm text-blue-700/70">
              Autores: Diputado A, Diputado B • Cámara de origen: Diputados
            </p>
            <p className="text-sm text-blue-900/80">
              Proyecto para mejorar la regulación del transporte público y la fiscalización.
            </p>
          </div>

          <div className="mt-4 grid sm:grid-cols-3 gap-3">
            {[
              { label: "A favor", value: "70%" },
              { label: "En contra", value: "20%" },
              { label: "Abstenciones", value: "10%" },
            ].map((x) => (
              <div key={x.label} className="rounded-xl border border-gray-200 p-3">
                <p className="text-xs uppercase tracking-wide text-blue-700/70">{x.label}</p>
                <p className="text-2xl font-semibold">{x.value}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Perfil parlamentario (mock) */}
        <Card title="Perfil de parlamentario">
          <div className="flex items-start gap-4">
            <div className="h-12 w-12 rounded-xl bg-blue-200" aria-hidden />
            <div className="flex-1">
              <p className="font-medium">Diputado Juan Pérez</p>
              <p className="text-sm text-blue-700/70">
                Partido: Independiente • Distrito: Santiago Centro
              </p>

              <div className="mt-4">
                <p className="text-sm font-semibold mb-2">Últimas Votaciones</p>
                <ul className="space-y-1 text-sm">
                  <li className="flex items-center justify-between rounded-lg border border-gray-200 px-3 py-2">
                    <span>Reforma a la Educación</span>
                    <Pill>✅ A favor</Pill>
                  </li>
                  <li className="flex items-center justify-between rounded-lg border border-gray-200 px-3 py-2">
                    <span>Ley de Transporte</span>
                    <Pill>❌ En contra</Pill>
                  </li>
                </ul>
              </div>
               {/* 🔗 Aquí está el link de navegación */}
              <Link
                to={`/parlamentarios/123`}
                className="mt-4 inline-block text-sm font-medium text-blue-700 hover:underline"
              >
                Ver perfil completo →
              </Link>
            </div>
          </div>
        </Card>
      </main>

      {/* Footer minimal */}
      <footer className="py-8 text-center text-xs text-blue-700/60">
        Datos públicos • Actualizado cada hora • MVP
      </footer>
    </div>
  );
}
