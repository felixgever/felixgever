export function formatCurrencyIls(amount: number): string {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(value?: string | null): string {
  if (!value) return "-";
  return new Date(value).toLocaleDateString("he-IL");
}
