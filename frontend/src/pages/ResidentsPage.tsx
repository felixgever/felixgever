import { FormEvent, useEffect, useState } from "react";
import type { CSSProperties } from "react";

import { createResident } from "../api/residents";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useProjects } from "../hooks/useProjects";
import { useResidents } from "../hooks/useResidents";

export function ResidentsPage() {
  const { data: projects } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>(undefined);
  const { data: residents, loading, error, run } = useResidents(selectedProjectId);

  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedProjectId && projects?.length) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

  async function onCreateResident(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedProjectId) return;
    setFormError(null);
    try {
      await createResident({
        project_id: selectedProjectId,
        full_name: fullName,
        phone: phone || undefined,
      });
      setFullName("");
      setPhone("");
      await run();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Failed to create resident");
    }
  }

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <h1>Residents Management</h1>
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
        <h3>Add resident</h3>
        <form onSubmit={onCreateResident} style={{ display: "flex", gap: 8 }}>
          <input
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            placeholder="Full name"
            required
          />
          <input
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
            placeholder="Phone"
          />
          <button type="submit">Add</button>
        </form>
        <ErrorState message={formError} />
      </article>

      <article style={boxStyle}>
        <h3>Residents list</h3>
        {loading ? <LoadingState /> : null}
        <ErrorState message={error} />
        <ul>
          {(residents ?? []).map((resident) => (
            <li key={resident.id}>
              {resident.full_name} | {resident.phone || "-"} | consent:{" "}
              {resident.consent_status}
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
