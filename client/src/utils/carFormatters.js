export function parseUsdPrice(value) {
  if (!value) return null;
  const digits = String(value).replace(/[^\d]/g, "");
  return digits ? Number(digits) : null;
}

export function formatMileage(value) {
  if (typeof value !== "number") return "Mileage N/A";
  return `${new Intl.NumberFormat("en-US").format(value)} km`;
}

export function formatPrice(value) {
  return value || "Price on request";
}

export function getOriginLabel(sourceKind) {
  if (!sourceKind) return "All Cars";
  if (sourceKind.includes("korean")) return "Korean";
  if (sourceKind.includes("foreign")) return "Imported";
  return "Inventory";
}
