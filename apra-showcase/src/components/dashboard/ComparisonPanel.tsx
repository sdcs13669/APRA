import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { useMultiAccuracyData } from "../../hooks/useMultiAccuracyData";
import type { ComparisonMode } from "../../hooks/useMultiAccuracyData";
import type { AttackMethod, DatasetType } from "../../types";
import { ATTACK_METHODS, DEFENSE_LABELS, ATTACK_LABELS } from "../../types";

const DEFENSE_COLORS: Record<string, string> = {
  apra: "#2563EB",
  avg: "#8B5CF6",
  clip: "#16A34A",
  deepsight: "#DC2626",
  foolsgold: "#F59E0B",
  rflbat: "#EC4899",
};

interface Props {
  selectedAttack: AttackMethod;
  dataset: DatasetType;
}

type TabId = "accuracy" | AttackMethod;

export default function ComparisonPanel({ selectedAttack, dataset }: Props) {
  const [tab, setTab] = useState<TabId>("accuracy");

  const mode: ComparisonMode =
    tab === "accuracy"
      ? { type: "accuracy", attack: selectedAttack }
      : { type: "asr", attack: tab as AttackMethod };

  const { data, series, loading } = useMultiAccuracyData(mode, dataset);

  const sampled = data.filter((_, i) => i % 10 === 0 || i === data.length - 1);

  const metricLabel = tab === "accuracy" ? "主任务准确率 (%)" : "ASR (%)";
  const title =
    tab === "accuracy"
      ? `6 种防御 · ${ATTACK_LABELS[selectedAttack]}`
      : `6 种防御 ASR · ${ATTACK_LABELS[tab as AttackMethod]}`;

  return (
    <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6">
      <h3
        className="text-sm font-semibold text-slate-800 mb-3"
        style={{ fontFamily: "'Lexend', sans-serif" }}
      >
        多方法对比
      </h3>

      {/* Tab selector */}
      <div className="flex items-center gap-1.5 flex-wrap mb-4">
        <button
          onClick={() => setTab("accuracy")}
          className={`px-2.5 py-1 text-xs rounded-full font-medium transition-colors ${
            tab === "accuracy"
              ? "bg-blue-600 text-white"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          }`}
        >
          总准确率
        </button>
        <span className="text-slate-300 text-xs">|</span>
        {ATTACK_METHODS.map((a) => (
          <button
            key={a}
            onClick={() => setTab(a)}
            className={`px-2.5 py-1 text-xs rounded-full font-medium transition-colors ${
              tab === a
                ? "bg-blue-600 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {ATTACK_LABELS[a]} ASR
          </button>
        ))}
      </div>

      {/* Chart */}
      {loading ? (
        <div className="h-[360px] flex items-center justify-center text-slate-400 text-sm">加载中...</div>
      ) : (
        <ResponsiveContainer width="100%" height={360}>
          <LineChart data={sampled}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis
              dataKey="epoch"
              stroke="#64748B"
              fontSize={12}
              tick={{ fill: "#64748B" }}
              label={{ value: "Epoch", position: "insideBottomRight", offset: -5, fill: "#64748B", fontSize: 12 }}
            />
            <YAxis
              domain={[0, 100]}
              stroke="#64748B"
              fontSize={12}
              tick={{ fill: "#64748B" }}
              label={{ value: metricLabel, angle: -90, position: "insideLeft", fill: "#64748B", fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#FFFFFF",
                border: "1px solid #E2E8F0",
                borderRadius: "8px",
                color: "#1E293B",
                boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
              }}
              formatter={(value: number, name: string) => [`${value.toFixed(1)}%`, DEFENSE_LABELS[name] ?? name]}
            />
            <Legend
              formatter={(value: string) => DEFENSE_LABELS[value] ?? value}
              wrapperStyle={{ fontSize: "12px" }}
            />
            {series.map((s) => (
              <Line
                key={s}
                type="monotone"
                dataKey={s}
                name={s}
                stroke={DEFENSE_COLORS[s] ?? "#94A3B8"}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
