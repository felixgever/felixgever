export function ErrorState({ message }: { message?: string | null }) {
  if (!message) return null;
  return (
    <p
      style={{
        color: "#b91c1c",
        background: "#fee2e2",
        border: "1px solid #fecaca",
        padding: "8px 12px",
        borderRadius: 6,
      }}
    >
      {message}
    </p>
  );
}
