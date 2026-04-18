import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

import { fetchBids } from "../api/domain";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useProjects } from "../hooks/useProjects";
import { formatCurrencyIls } from "../utils/format";

export function DeveloperBidsPage() {
  const { data: projects } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<number | undefined>(undefined);
  const [bids, setBids] = useState<
    Array<{
      id: number;
      developer_name: string;
      proposal_summary?: string | null;
      score?: number | null;
      price_offer_ils?: number | null;
      status: string;
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
    async function loadBids() {
      if (!selectedProjectId) return;
      setLoading(true);
      setError(null);
      try {
        const data = await fetchBids(selectedProjectId);
        setBids(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load bids");
      } finally {
        setLoading(false);
      }
    }
    void loadBids();
  }, [selectedProjectId]);

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <h1>Developer Tender</h1>
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
        <h3>Bids comparison</h3>
        {loading ? <LoadingState /> : null}
        <ErrorState message={error} />
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={thStyle}>Developer</th>
              <th style={thStyle}>Price Offer</th>
              <th style={thStyle}>Score</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Summary</th>
            </tr>
          </thead>
          <tbody>
            {bids.map((bid) => (
              <tr key={bid.id}>
                <td style={tdStyle}>{bid.developer_name}</td>
                <td style={tdStyle}>
                  {typeof bid.price_offer_ils === "number"
                    ? formatCurrencyIls(bid.price_offer_ils)
                    : "-"}
                </td>
                <td style={tdStyle}>{bid.score ?? "-"}</td>
                <td style={tdStyle}>{bid.status}</td>
                <td style={tdStyle}>{bid.proposal_summary ?? "-"}</td>
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
