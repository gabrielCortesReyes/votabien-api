// /src/main.jsx
// /npm run dev
// /http://localhost:5173

import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import WireframeLegislativo from "./WireframeLegislativo.jsx";
import ProyectoDetalle from "./pages/ProyectoDetalle.jsx";
import ParlamentarioDetalle from "./pages/ParlamentarioDetalle.jsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<WireframeLegislativo />} />
        <Route path="/proyectos/:id" element={<ProyectoDetalle />} />
        <Route path="/parlamentarios/:id" element={<ParlamentarioDetalle />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
