import type { DefenseMethod, AttackMethod } from "../types";

export function getAccuracyCsvPath(defense: DefenseMethod, attack: AttackMethod): string {
  return `/data/accuracy/${defense}_${attack}.csv`;
}

export function getTrajectoryCsvPath(defense: DefenseMethod, attack: AttackMethod): string {
  return `/data/trajectory/${defense}_${attack}.csv`;
}

export function getSummaryPath(): string {
  return "/data/accuracy/summary.json";
}

export function getTracePath(attack?: AttackMethod): string {
  if (attack) return `/data/apra_client_trace_${attack}.csv`;
  return "/data/apra_client_trace.csv";
}

export function getRoundSummaryPath(attack?: AttackMethod): string {
  if (attack) return `/data/apra_round_summary_${attack}.csv`;
  return "/data/apra_round_summary.csv";
}
