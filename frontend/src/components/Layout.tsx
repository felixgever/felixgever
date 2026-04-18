import type { PropsWithChildren } from "react";
import { Link, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/projects", label: "Projects" },
  { to: "/residents", label: "Residents" },
  { to: "/signatures", label: "Signatures" },
  { to: "/workflow", label: "Workflow" },
  { to: "/bids", label: "Developer Bids" },
  { to: "/planning", label: "Planning & Docs" },
  { to: "/billing", label: "Billing" },
  { to: "/resident-portal", label: "Resident Portal" },
];

export function Layout({ children }: PropsWithChildren) {
  const { user, logout } = useAuth();
  const location = useLocation();

  return (
    <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", minHeight: "100vh" }}>
      <aside style={{ background: "#0f172a", color: "#fff", padding: 16 }}>
        <h2 style={{ marginTop: 0 }}>Urban Renewal</h2>
        <p style={{ opacity: 0.85, fontSize: 12 }}>
          {user?.full_name ?? "Guest"}
          <br />
          {user?.roles?.map((role) => role.name).join(", ") || ""}
        </p>
        <nav style={{ display: "grid", gap: 8 }}>
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              style={{
                color: "#fff",
                textDecoration: location.pathname === item.to ? "underline" : "none",
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <button style={{ marginTop: 24 }} onClick={logout}>
          Logout
        </button>
      </aside>
      <main style={{ padding: 24, background: "#f8fafc" }}>{children}</main>
    </div>
  );
}
