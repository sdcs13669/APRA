import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useApraTrace } from "../../hooks/useApraTrace";
import { useMemo } from "react";
import type { AttackMethod, DatasetType } from "../../types";

interface Props {
  attack: AttackMethod;
  dataset: DatasetType;
}

export default function FilterStatsChart({ attack, dataset }: Props) {
  const { frames } = useApraTrace(attack, dataset);

  const chartData = useMemo(() => {
    return frames
      .filter((_, i) => i % 5 === 0)
      .map((frame) => {
        const madIds = (() => {
          try { return JSON.parse(frame.roundSummary.mad_pass_ids) as number[]; } catch { return []; }
        })();
        const clusterIds = (() => {
          try { return JSON.parse(frame.roundSummary.cluster_pass_ids) as number[]; } catch { return []; }
        })();
        const finalIds = (() => {
          try { return JSON.parse(frame.roundSummary.final_selected_ids) as number[]; } catch { return []; }
        })();

        return {
          epoch: frame.roundSummary.epoch,
          "MAD通过": madIds.length,
          "聚类通过": clusterIds.length,
          "最终采用": finalIds.length,
        };
      });
  }, [frames]);

  return (
    <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6">
      <h3 className="text-sm mb-4 text-slate-800" style={{ fontFamily: "'Lexend', sans-serif" }}>
        APRA 各阶段过滤统计
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
          <XAxis dataKey="epoch" stroke="#64748B" fontSize={10} tick={{ fill: "#64748B" }} />
          <YAxis stroke="#64748B" fontSize={10} tick={{ fill: "#64748B" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #E2E8F0",
              borderRadius: "8px",
              color: "#1E293B",
            }}
          />
          <Bar dataKey="MAD通过" stackId="filter" fill="#93C5FD" />
          <Bar dataKey="聚类通过" stackId="filter" fill="#2563EB" />
          <Bar dataKey="最终采用" stackId="filter" fill="#16A34A" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
