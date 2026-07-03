import type { DefenseMethod, AttackMethod, DatasetType } from "../types";

export function getAccuracyCsvPath(defense: DefenseMethod, attack: AttackMethod, dataset: DatasetType): string {
  return `/data/accuracy/${dataset}_${defense}_${attack}.csv`;
}

export function getTrajectoryCsvPath(defense: DefenseMethod, attack: AttackMethod, dataset: DatasetType): string {
  return `/data/trajectory/${dataset}_${defense}_${attack}.csv`;
}

export function getSummaryPath(dataset?: DatasetType): string {
  if (dataset) return `/data/accuracy/summary_${dataset}.json`;
  return "/data/accuracy/summary.json";
}

export function getTracePath(attack: AttackMethod, dataset: DatasetType): string {
  return `/data/apra_client_trace_${dataset}_${attack}.csv`;
}

export function getRoundSummaryPath(attack: AttackMethod, dataset: DatasetType): string {
  return `/data/apra_round_summary_${dataset}_${attack}.csv`;
}
