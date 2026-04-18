import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

import { fetchDocuments, fetchPlans } from "../api/domain";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useProjects } from "../hooks/useProjects";

export function PlanningDocumentsPage() {
  const { data: projects } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>(undefined);
  const [plans, setPlans] = useState<
    Array<{ id: number; name: string; zoning_status: string; feasibility_score?: number | null }>
  >([]);
  const [documents, setDocuments] = useState<
    Array<{ id: number; title: string; category: string; visibility: string }>
  >([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedProjectId && projects?.length) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

  useEffect(() => {
    async function loadData() {
      if (!selectedProjectId) return;
      setLoading(true);
      setError(null);
      try {
        const [planData, docsData] = await Promise.all([
          fetchPlans(selectedProjectId),
          fetchDocuments(selectedProjectId),
        ]);
        setPlans(planData);
        setDocuments(docsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load planning data");
      } finally {
        setLoading(false);
      }
    }
    void loadData();
  }, [selectedProjectId]);

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <h1>Planning & Documents</h1>
      <article style={boxStyle}>
        <label>
          Project:
          <select
            value={selectedProjectId ?? ""}
            onChange={(event) => setSelectedProjectId(Number(event.target.value))}
          >
            {(projects ?? []).map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </label>
      </article>
      <article style={boxStyle}>
        <h3>Planning & feasibility</h3>
        {loading ? <LoadingState /> : null}
        <ErrorState message={error} />
        <ul>
          {plans.map((plan) => (
            <li key={plan.id}>
              {plan.name} | zoning: {plan.zoning_status} | feasibility score:{" "}
              {plan.feasibility_score ?? "-"}
            </li>
          ))}
        </ul>
      </article>
      <article style={boxStyle}>
        <h3>Document management</h3>
        <ul>
          {documents.map((document) => (
            <li key={document.id}>
              {document.title} | category: {document.category} | visibility: {document.visibility}
            </li>
          ))}
        </ul>
      </article>
    </section>
  );
}

const boxStyle: CSSProperties = {
  background: "#fff",
  borderRadius: 8,
  padding: 16,
};
