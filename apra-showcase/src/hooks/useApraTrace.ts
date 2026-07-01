import { useState, useEffect } from "react";
import type { ApraClientTraceRow, ApraRoundSummaryRow, ReplayFrame, AttackMethod } from "../types";
import { getTracePath, getRoundSummaryPath } from "../lib/data-paths";
import { parseCsv } from "../lib/csv";

export function useApraTrace(attack?: AttackMethod) {
  const [frames, setFrames] = useState<ReplayFrame[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch(getTracePath(attack)).then((r) => r.text()),
      fetch(getRoundSummaryPath(attack)).then((r) => r.text()),
    ])
      .then(([traceText, summaryText]) => {
        const rawTraces = parseCsv<Record<string, string>>(traceText);
        const clientTraces: ApraClientTraceRow[] = rawTraces.map((row) => ({
          epoch: Number(row.epoch),
          client_id: Number(row.client_id),
          role: row.role as "malicious" | "benign",
          is_adversary: Number(row.is_adversary),
          update_norm: Number(row.update_norm),
          mad_z_score: Number(row.mad_z_score),
          mad_pass: Number(row.mad_pass),
          mad_effective_pass: Number(row.mad_effective_pass),
          cluster_label: Number(row.cluster_label),
          selected_cluster: Number(row.selected_cluster),
          cluster_pass: Number(row.cluster_pass),
          cluster_effective_pass: Number(row.cluster_effective_pass),
          final_selected: Number(row.final_selected),
          trust_weight: Number(row.trust_weight),
          clip_factor: Number(row.clip_factor),
        }));

        const rawSummaries = parseCsv<Record<string, string>>(summaryText);
        const summaries: ApraRoundSummaryRow[] = rawSummaries.map((row) => ({
          epoch: Number(row.epoch),
          num_sampled: Number(row.num_sampled),
          num_adversaries: Number(row.num_adversaries),
          mad_pass_ids: row.mad_pass_ids,
          mad_reject_ids: row.mad_reject_ids,
          mad_k: Number(row.mad_k),
          mad_safety_keep_used: Number(row.mad_safety_keep_used),
          cluster_best_k: Number(row.cluster_best_k),
          cluster_selected_cluster: Number(row.cluster_selected_cluster),
          cluster_pass_ids: row.cluster_pass_ids,
          cluster_reject_ids: row.cluster_reject_ids,
          final_selected_ids: row.final_selected_ids,
          final_rejected_ids: row.final_rejected_ids,
          final_selected_benign_count: Number(row.final_selected_benign_count),
          final_selected_malicious_count: Number(row.final_selected_malicious_count),
        }));

        const summaryMap = new Map(summaries.map((s) => [s.epoch, s]));
        const traceMap = new Map<number, ApraClientTraceRow[]>();
        clientTraces.forEach((trace) => {
          if (!traceMap.has(trace.epoch)) {
            traceMap.set(trace.epoch, []);
          }
          traceMap.get(trace.epoch)!.push(trace);
        });

        const frames: ReplayFrame[] = [];
        summaryMap.forEach((roundSummary, epoch) => {
          frames.push({
            roundSummary,
            clientTraces: traceMap.get(epoch) ?? [],
          });
        });
        frames.sort((a, b) => a.roundSummary.epoch - b.roundSummary.epoch);
        setFrames(frames);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [attack]);

  return { frames, loading, error };
}
