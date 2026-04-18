import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

import { fetchWorkflowStages } from "../api/domain";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useProjects } from "../hooks/useProjects";

export function WorkflowPage() {
  const { data: projects } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>(undefined);
  const [stages, setStages] = useState<
    Array<{ id: number; stage_key: string; status: string; started_at?: string | null }>
  >([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedProjectId && projects?.length) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

  useEffect(() => {
    async function loadStages() {
      if (!selectedProjectId) return;
      setLoading(true);
      setError(null);
      try {
        const data = await fetchWorkflowStages(selectedProjectId);
        setStages(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load workflow");
      } finally {
        setLoading(false);
      }
    }
    void loadStages();
  }, [selectedProjectId]);

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <h1>Workflow Stages</h1>
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
        <h3>Organizer Law stages</h3>
        {loading ? <LoadingState /> : null}
        <ErrorState message={error} />
        <ol>
          {stages.map((stage) => (
            <li key={stage.id}>
              {stage.stage_key} — <strong>{stage.status}</strong> — started:{" "}
              {stage.started_at ? new Date(stage.started_at).toLocaleString() : "-"}
            </li>
          ))}
        </ol>
      </article>
    </section>
  );
}

const boxStyle: CSSProperties = {
  background: "#fff",
  borderRadius: 8,
  padding: 16,
};
