import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { TableProvider } from "./contexts/TableContext";
import Sessions from "./pages/Sessions";
import Matching from "./pages/Matching";
import Home from "./pages/Home";
import Skills from "./pages/Skills";
import Register from "./pages/Register";

function App() {
  return (
    <TableProvider>
      <div className="app-container">
        <main className="app-main">
          <Routes>
            <Route path="/sessions" element={<Sessions />} />
            <Route path="/matching" element={<Matching />} />
            <Route path="/home" element={<Home />} />
            <Route path="/skills" element={<Skills />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="*" element={<Navigate to="/home" replace />} />
          </Routes>
        </main>
      </div>
    </TableProvider>
  );
}
export default App;
