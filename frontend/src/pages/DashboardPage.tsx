import { useMemo } from "react";
import type { CSSProperties } from "react";

import { LoadingState } from "../components/LoadingState";
import { useAuth } from "../context/AuthContext";
import { useProjects } from "../hooks/useProjects";
import { formatCurrencyIls } from "../utils/format";

export function DashboardPage() {
  const { user } = useAuth();
  const { data: projects, loading } = useProjects();

  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const roleLabel = roleNames.join(", ");

  const stats = useMemo(() => {
    const projectList = projects ?? [];
    const units = projectList.flatMap((project) => project.units);
    const estimatedRevenue = projectList.reduce(
      (total, project) => total + project.per_unit_price_ils * project.units.length,
      0,
    );
    return {
      projectCount: projectList.length,
      unitCount: units.length,
      estimatedRevenue,
    };
  }, [projects]);

  if (loading) return <LoadingState label="Loading dashboard..." />;

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div>
        <h1 style={{ marginBottom: 4 }}>Dashboard</h1>
        <p style={{ margin: 0, color: "#334155" }}>
          Role view: <strong>{roleLabel || "unknown"}</strong>
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        <article style={cardStyle}>
          <h3>Projects</h3>
          <strong>{stats.projectCount}</strong>
        </article>
        <article style={cardStyle}>
          <h3>Existing Units</h3>
          <strong>{stats.unitCount}</strong>
        </article>
        <article style={cardStyle}>
          <h3>Estimated Developer Billing</h3>
          <strong>{formatCurrencyIls(stats.estimatedRevenue)}</strong>
        </article>
      </div>

      <article style={cardStyle}>
        <h3>Role-tailored actions</h3>
        <ul>
          {roleNames.includes("organizer") ? (
            <li>Manage residents, signatures, and workflow up to Developer Selection.</li>
          ) : null}
          {roleNames.includes("developer") ? (
            <li>Review tender bids, submit proposals, and activate per-unit payments.</li>
          ) : null}
          {roleNames.includes("professional") ? (
            <li>Access planning, feasibility, and legal/document collaboration tools.</li>
          ) : null}
          {roleNames.includes("resident") ? (
            <li>Track project updates, documents, and signature requests in the portal.</li>
          ) : null}
          {roleNames.includes("admin") ? (
            <li>Audit platform activity and control billing plans/subscriptions.</li>
          ) : null}
        </ul>
      </article>
    </section>
  );
}

const cardStyle: CSSProperties = {
  background: "#fff",
  borderRadius: 8,
  padding: 16,
  boxShadow: "0 1px 2px rgba(15,23,42,0.08)",
};
