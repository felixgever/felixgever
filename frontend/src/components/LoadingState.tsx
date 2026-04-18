export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return <p style={{ color: "#475569" }}>{label}</p>;
}
