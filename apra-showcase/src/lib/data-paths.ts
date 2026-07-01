import type { DefenseMethod, AttackMethod } from "../types";

export function getAccuracyCsvPath(defense: DefenseMethod, attack: AttackMethod): string {
  return `/data/accuracy/${defense}_${attack}.csv`;
}

export function getSummaryPath(): string {
  return "/data/accuracy/summary.json";
}

export function getTracePath(): string {
  return "/data/apra_client_trace.csv";
}

export function getRoundSummaryPath(): string {
  return "/data/apra_round_summary.csv";
}
