import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { useAccuracyData } from "../../hooks/useAccuracyData";
import type { DefenseMethod, AttackMethod } from "../../types";
import { DEFENSE_LABELS } from "../../types";

interface Props {
  selectedDefense: DefenseMethod;
  selectedAttack: AttackMethod;
}

export default function AsrChart({ selectedDefense, selectedAttack }: Props) {
  const { data } = useAccuracyData(selectedDefense, selectedAttack);
  const sampledData = data.filter((_, i) => i % 10 === 0 || i === data.length - 1);

  return (
    <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6">
      <h3 className="text-sm mb-4 text-slate-800" style={{ fontFamily: "'Lexend', sans-serif" }}>
        后门攻击成功率 (ASR) 曲线
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={sampledData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
          <XAxis dataKey="epoch" stroke="#64748B" fontSize={11} tick={{ fill: "#64748B" }} />
          <YAxis domain={[0, 100]} stroke="#64748B" fontSize={11} tick={{ fill: "#64748B" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #E2E8F0",
              borderRadius: "8px",
              color: "#1E293B",
            }}
            formatter={(value) => [`${Number(value).toFixed(1)}%`, ""]}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="bkd_acc"
            name={`${DEFENSE_LABELS[selectedDefense]} ASR`}
            stroke="#DC2626"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
