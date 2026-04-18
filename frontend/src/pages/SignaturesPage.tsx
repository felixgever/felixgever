import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

import { fetchSignatures } from "../api/domain";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useProjects } from "../hooks/useProjects";

export function SignaturesPage() {
  const { data: projects } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>(undefined);
  const [signatures, setSignatures] = useState<
    Array<{
      id: number;
      resident_id: number;
      status: string;
      signature_provider: string;
      signed_at?: string | null;
    }>
  >([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedProjectId && projects?.length) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

  useEffect(() => {
    async function loadSignatures() {
      if (!selectedProjectId) return;
      setLoading(true);
      setError(null);
      try {
        const data = await fetchSignatures(selectedProjectId);
        setSignatures(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load signatures");
      } finally {
        setLoading(false);
      }
    }
    void loadSignatures();
  }, [selectedProjectId]);

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <h1>Signatures Overview</h1>
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
        <h3>Signature requests</h3>
        {loading ? <LoadingState /> : null}
        <ErrorState message={error} />
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={thStyle}>ID</th>
              <th style={thStyle}>Resident</th>
              <th style={thStyle}>Provider</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Signed At</th>
            </tr>
          </thead>
          <tbody>
            {signatures.map((signature) => (
              <tr key={signature.id}>
                <td style={tdStyle}>{signature.id}</td>
                <td style={tdStyle}>{signature.resident_id}</td>
                <td style={tdStyle}>{signature.signature_provider}</td>
                <td style={tdStyle}>{signature.status}</td>
                <td style={tdStyle}>{signature.signed_at ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </section>
  );
}

const boxStyle: CSSProperties = {
  background: "#fff",
  borderRadius: 8,
  padding: 16,
};

const thStyle: CSSProperties = {
  textAlign: "left",
  borderBottom: "1px solid #e2e8f0",
  padding: "8px 6px",
};

const tdStyle: CSSProperties = {
  borderBottom: "1px solid #f1f5f9",
  padding: "8px 6px",
};
