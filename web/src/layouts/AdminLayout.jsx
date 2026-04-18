import { Outlet } from "react-router-dom";
import { useState } from "react";
import Sidebar from "../components/admin/Sidebar";
import Header from "../components/admin/Header";

export default function AdminLayout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex" style={{ height: "100vh" }}>
      {/* Sidebar — alto fijo, no crece ni shrink */}
      <div className="flex-shrink-0">
        <Sidebar collapsed={collapsed} onCollapse={setCollapsed} />
      </div>

      {/* Zona derecha — ocupa el resto, scroll solo aquí */}
      <div className="flex flex-col flex-1 min-w-0" style={{ height: "100vh" }}>
        {/* Header pegado arriba */}
        <div className="flex-shrink-0">
          <Header onToggleSidebar={() => setCollapsed((p) => !p)} />
        </div>

        {/* Content area — único lugar que hace scroll */}
        <main className="flex-1 overflow-y-auto bg-[var(--color-neutral-bg)] p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}