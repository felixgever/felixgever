import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

import { fetchDocuments, fetchMessages, fetchSignatures } from "../api/domain";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useProjects } from "../hooks/useProjects";

export function ResidentPortalPage() {
  const { data: projects } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>(undefined);
  const [documents, setDocuments] = useState<Array<{ id: number; title: string }>>([]);
  const [signatures, setSignatures] = useState<Array<{ id: number; status: string }>>([]);
  const [messages, setMessages] = useState<Array<{ id: number; body: string; channel: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedProjectId && projects?.length) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

  useEffect(() => {
    async function loadPortalData() {
      if (!selectedProjectId) return;
      setLoading(true);
      setError(null);
      try {
        const [docs, sigs, msgs] = await Promise.all([
          fetchDocuments(selectedProjectId),
          fetchSignatures(selectedProjectId),
          fetchMessages(selectedProjectId),
        ]);
        setDocuments(docs);
        setSignatures(sigs);
        setMessages(msgs);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load resident portal");
      } finally {
        setLoading(false);
      }
    }
    void loadPortalData();
  }, [selectedProjectId]);

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <h1>Resident Portal</h1>
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
        <h3>My signature status</h3>
        {loading ? <LoadingState /> : null}
        <ErrorState message={error} />
        <ul>
          {signatures.map((signature) => (
            <li key={signature.id}>
              Request #{signature.id} - <strong>{signature.status}</strong>
            </li>
          ))}
        </ul>
      </article>
      <article style={boxStyle}>
        <h3>Shared project documents</h3>
        <ul>
          {documents.map((document) => (
            <li key={document.id}>{document.title}</li>
          ))}
        </ul>
      </article>
      <article style={boxStyle}>
        <h3>Recent updates</h3>
        <ul>
          {messages.map((message) => (
            <li key={message.id}>
              [{message.channel}] {message.body}
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
