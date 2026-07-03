import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { useAccuracyData } from "../../hooks/useAccuracyData";
import type { DefenseMethod, AttackMethod, DatasetType } from "../../types";
import { DEFENSE_LABELS } from "../../types";

interface Props {
  selectedDefense: DefenseMethod;
  selectedAttack: AttackMethod;
  dataset: DatasetType;
}

export default function CombinedChart({ selectedDefense, selectedAttack, dataset }: Props) {
  const { data } = useAccuracyData(selectedDefense, selectedAttack, dataset);
  const sampled = data.filter((_, i) => i % 10 === 0 || i === data.length - 1);

  return (
    <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6">
      <h3 className="text-sm font-semibold text-slate-800 mb-4" style={{ fontFamily: "'Lexend', sans-serif" }}>
        {DEFENSE_LABELS[selectedDefense]} — 准确率 &amp; ASR 曲线
      </h3>
      <ResponsiveContainer width="100%" height={360}>
        <LineChart data={sampled}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
          <XAxis dataKey="epoch" stroke="#64748B" fontSize={12} tick={{ fill: "#64748B" }} />
          <YAxis yAxisId="left" domain={[0, 100]} stroke="#64748B" fontSize={12} tick={{ fill: "#64748B" }} />
          <YAxis yAxisId="right" orientation="right" domain={[0, 100]} stroke="#64748B" fontSize={12} tick={{ fill: "#64748B" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #E2E8F0",
              borderRadius: "8px",
              color: "#1E293B",
              boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
            }}
            formatter={(value: number) => [`${value.toFixed(1)}%`, ""]}
          />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="test_acc"
            name="主任务准确率"
            stroke="#2563EB"
            strokeWidth={2}
            dot={false}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="bkd_acc"
            name="后门攻击成功率 (ASR)"
            stroke="#DC2626"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
