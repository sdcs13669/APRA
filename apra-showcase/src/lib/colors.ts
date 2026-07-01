import type { DefenseMethod } from "../types";

export const CHART_COLORS: Record<DefenseMethod, string> = {
  apra: "var(--chart-line-1)",
  avg: "var(--chart-line-2)",
  clip: "var(--chart-line-3)",
  deepsight: "var(--chart-line-4)",
  foolsgold: "var(--chart-line-5)",
  rflbat: "var(--chart-line-6)",
};

export const CLIENT_STATUS_COLORS = {
  benignPass: "#22C55E",
  maliciousPass: "#DC2626",
  madReject: "#6B7280",
  clusterReject: "#F97316",
  madFlash: "#F59E0B",
  clusterFlash: "#8B5CF6",
} as const;

export const HEATMAP_COLORS = {
  low: "#22C55E",
  medium: "#F59E0B",
  high: "#DC2626",
} as const;
