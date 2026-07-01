import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from "recharts";
import { useMemo } from "react";
import type { AccuracyRow } from "../../types";

interface Props {
  accuracyData: AccuracyRow[];
  currentRound: number;
}

export default function AccuracyTrend({ accuracyData, currentRound }: Props) {
  const chartData = useMemo(() => {
    return accuracyData
      .filter((row) => row.epoch <= currentRound)
      .filter((_, i) => i % 5 === 0)
      .map((row) => ({
        epoch: row.epoch,
        accuracy: row.test_acc,
        asr: row.bkd_acc,
      }));
  }, [accuracyData, currentRound]);

  return (
    <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6">
      <h3 className="text-sm mb-4 text-slate-800" style={{ fontFamily: "'Lexend', sans-serif" }}>
        全局模型精度趋势
      </h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
          <XAxis dataKey="epoch" stroke="#64748B" fontSize={10} tick={{ fill: "#64748B" }} />
          <YAxis domain={[0, 100]} stroke="#64748B" fontSize={10} tick={{ fill: "#64748B" }} />
          <Legend />
          <Line type="monotone" dataKey="accuracy" name="准确率" stroke="#2563EB" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="asr" name="ASR" stroke="#DC2626" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
