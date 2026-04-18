import { FormEvent, useEffect, useState } from "react";
import type { CSSProperties } from "react";
import { useParams } from "react-router-dom";

import { addUnit, fetchProject } from "../api/projects";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import type { Project } from "../types";

export function ProjectDetailsPage() {
  const { projectId } = useParams();
  const numericProjectId = Number(projectId);
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newUnitNumber, setNewUnitNumber] = useState("");

  async function loadProject() {
    if (!numericProjectId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProject(numericProjectId);
      setProject(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadProject();
  }, [numericProjectId]);

  async function onAddUnit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!newUnitNumber || !project) return;
    setError(null);
    try {
      await addUnit(project.id, { unit_number: newUnitNumber });
      setNewUnitNumber("");
      await loadProject();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add unit");
    }
  }

  if (!projectId) return <p>Project id missing.</p>;
  if (loading) return <LoadingState label="Loading project..." />;

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <header>
        <h1>{project?.name ?? "Project details"}</h1>
        <p>
          Stage: <strong>{project?.current_stage}</strong> | Developer payment required:{" "}
          <strong>{project?.developer_payment_required ? "Yes" : "No"}</strong>
        </p>
      </header>
      <ErrorState message={error} />
      <article style={boxStyle}>
        <h3>Project metadata</h3>
        <p>City: {project?.city}</p>
        <p>Address: {project?.address || "-"}</p>
        <p>Per-unit price: {project?.per_unit_price_ils} ₪</p>
      </article>
      <article style={boxStyle}>
        <h3>Units</h3>
        <form onSubmit={onAddUnit} style={{ display: "flex", gap: 8 }}>
          <input
            value={newUnitNumber}
            onChange={(event) => setNewUnitNumber(event.target.value)}
            placeholder="Add unit number"
            required
          />
          <button type="submit">Add unit</button>
        </form>
        <ul>
          {(project?.units ?? []).map((unit) => (
            <li key={unit.id}>
              Unit {unit.unit_number} | Floor: {unit.floor ?? "-"} | Residents:{" "}
              {unit.residents_count}
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
