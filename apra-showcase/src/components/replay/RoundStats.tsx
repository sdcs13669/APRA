import type { ApraRoundSummaryRow } from "../../types";

interface Props {
  roundSummary: ApraRoundSummaryRow;
}

export default function RoundStats({ roundSummary }: Props) {
  const madPassCount = (() => {
    try { return (JSON.parse(roundSummary.mad_pass_ids) as number[]).length; } catch { return 0; }
  })();

  return (
    <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6 space-y-4">
      <h3 className="text-sm text-slate-800" style={{ fontFamily: "'Lexend', sans-serif" }}>
        实时统计
      </h3>

      <div>
        <p className="text-xs text-slate-500" style={{ fontFamily: "'Lexend', sans-serif" }}>MAD 预过滤</p>
        <p className="text-sm text-slate-700">
          通过 {madPassCount} / {roundSummary.num_sampled}
          <span className="text-slate-400 ml-2">k = {roundSummary.mad_k?.toFixed(2) ?? "N/A"}</span>
          {roundSummary.mad_safety_keep_used ? (
            <span className="text-green-600 ml-2">SAFETY KEEP</span>
          ) : null}
        </p>
      </div>

      <div>
        <p className="text-xs text-slate-500" style={{ fontFamily: "'Lexend', sans-serif" }}>层次聚类</p>
        <p className="text-sm text-slate-700">
          K = {roundSummary.cluster_best_k ?? "N/A"}
          <span className="text-slate-400 ml-2">
            Selected Cluster: {roundSummary.cluster_selected_cluster ?? "N/A"}
          </span>
        </p>
      </div>

      <div className="border-t border-[#E2E8F0] pt-4">
        <p className="text-xs text-slate-500" style={{ fontFamily: "'Lexend', sans-serif" }}>最终采用</p>
        <p className="text-sm">
          <span className="text-green-600 font-bold">
            良性 {roundSummary.final_selected_benign_count}
          </span>
          <span className="mx-2 text-slate-400">/</span>
          <span className="text-red-600 font-bold">
            恶意 {roundSummary.final_selected_malicious_count}
          </span>
        </p>
      </div>
    </div>
  );
}
