import { FormEvent, useState } from "react";
import type { CSSProperties } from "react";
import { Link } from "react-router-dom";

import { createProject } from "../api/projects";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useProjects } from "../hooks/useProjects";

export function ProjectsPage() {
  const { data: projects, loading, error, run } = useProjects();
  const [name, setName] = useState("");
  const [city, setCity] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setSubmitting(true);
    try {
      await createProject({ name, city });
      setName("");
      setCity("");
      await run();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Failed to create project");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <header>
        <h1>Projects</h1>
        <p>Manage urban renewal projects from identification to occupancy.</p>
      </header>

      <article style={boxStyle}>
        <h3>Create project</h3>
        <form onSubmit={onCreate} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <input
            placeholder="Project name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            required
          />
          <input
            placeholder="City"
            value={city}
            onChange={(event) => setCity(event.target.value)}
            required
          />
          <button type="submit" disabled={submitting}>
            {submitting ? "Creating..." : "Create"}
          </button>
        </form>
        <ErrorState message={formError} />
      </article>

      <article style={boxStyle}>
        <h3>Project list</h3>
        {loading ? <LoadingState /> : null}
        <ErrorState message={error} />
        <ul>
          {(projects ?? []).map((project) => (
            <li key={project.id}>
              <Link to={`/projects/${project.id}`}>{project.name}</Link> — {project.city} —
              stage: <strong>{project.current_stage}</strong> — units: {project.units.length}
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
