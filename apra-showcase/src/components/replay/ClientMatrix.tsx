import type { ApraClientTraceRow, ApraRoundSummaryRow } from "../../types";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";

interface Props {
  roundSummary: ApraRoundSummaryRow;
  clientTraces: ApraClientTraceRow[];
}

const COLORS = {
  benignPass: "#22C55E",
  maliciousPass: "#DC2626",
  madReject: "#6B7280",
  clusterReject: "#F97316",
};

export default function ClientMatrix({ roundSummary, clientTraces }: Props) {
  return (
    <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6">
      <h3 className="text-sm mb-4 text-slate-800" style={{ fontFamily: "'Lexend', sans-serif" }}>
        客户端状态矩阵 · Round {roundSummary.epoch}
      </h3>

      <div className="grid grid-cols-10 gap-2">
        {clientTraces.map((trace) => {
          let color = COLORS.benignPass;
          let label = "良性通过";

          if (trace.is_adversary && trace.final_selected) {
            color = COLORS.maliciousPass;
            label = "恶意漏检";
          } else if (!trace.mad_pass) {
            color = COLORS.madReject;
            label = "MAD 过滤";
          } else if (!trace.cluster_pass) {
            color = COLORS.clusterReject;
            label = "聚类过滤";
          } else if (trace.is_adversary && !trace.final_selected) {
            color = COLORS.clusterReject;
            label = "聚类过滤";
          }

          return (
            <TooltipProvider key={trace.client_id}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div
                    className="aspect-square rounded cursor-pointer transition-all hover:scale-110 hover:z-10"
                    style={{ backgroundColor: color }}
                  />
                </TooltipTrigger>
                <TooltipContent className="bg-white border border-[#E2E8F0] text-xs p-3 text-slate-800 shadow-sm">
                  <p>Client #{trace.client_id}</p>
                  <p>Role: {trace.role === "malicious" ? "Malicious" : "Benign"}</p>
                  <p>Update Norm: {trace.update_norm?.toFixed(3) ?? "N/A"}</p>
                  <p>MAD Z-Score: {trace.mad_z_score?.toFixed(2) ?? "N/A"}</p>
                  <p>Trust Weight: {trace.trust_weight?.toFixed(3) ?? "N/A"}</p>
                  <p>Status: {label}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          );
        })}
      </div>

      <div className="flex gap-4 mt-4 text-[10px] text-slate-500 flex-wrap">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded" style={{ backgroundColor: COLORS.benignPass }} /> 良性通过
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded" style={{ backgroundColor: COLORS.maliciousPass }} /> 恶意漏检
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded" style={{ backgroundColor: COLORS.madReject }} /> MAD 过滤
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded" style={{ backgroundColor: COLORS.clusterReject }} /> 聚类过滤
        </span>
      </div>
    </div>
  );
}
