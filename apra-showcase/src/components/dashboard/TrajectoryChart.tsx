import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { DefenseMethod, AttackMethod, DatasetType } from "../../types";
import { useTrajectoryData } from "../../hooks/useTrajectoryData";
import { ATTACK_METHODS, ATTACK_LABELS } from "../../types";

interface Props {
  selectedDefense: DefenseMethod;
  selectedAttack: AttackMethod;
  dataset: DatasetType;
}

export default function TrajectoryChart({ selectedDefense, selectedAttack, dataset }: Props) {
  const { data, loading, error } = useTrajectoryData(selectedDefense, selectedAttack, dataset);

  if (loading) {
    return (
      <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6">
        <h3 className="text-sm mb-4 text-slate-800" style={{ fontFamily: "'Lexend', sans-serif" }}>
          模型轨迹漂移
        </h3>
        <div className="h-64 flex items-center justify-center text-slate-500">Loading...</div>
      </div>
    );
  }

  if (error || data.length === 0) {
    return (
      <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6">
        <h3 className="text-sm mb-4 text-slate-800" style={{ fontFamily: "'Lexend', sans-serif" }}>
          模型轨迹漂移
        </h3>
        <div className="h-64 flex items-center justify-center text-slate-500 text-xs">
          {error ? `数据加载失败: ${error}` : "该实验无轨迹数据"}
        </div>
      </div>
    );
  }

  // Sample every 5 epochs for performance
  const sampled = data.filter((d) => d.epoch % 5 === 0 || d.epoch === data[0]?.epoch || d.epoch === data[data.length - 1]?.epoch);

  return (
    <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6">
      <h3 className="text-sm mb-4 text-slate-800" style={{ fontFamily: "'Lexend', sans-serif" }}>
        模型轨迹漂移 (Trajectory Drift)
      </h3>
      <div className="text-[10px] text-slate-500 mb-2">
        Cosine 相似度 (越高越稳定) · L2 距离 (越低越稳定)
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={sampled}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
          <XAxis
            dataKey="epoch"
            tick={{ fontSize: 10 }}
            label={{ value: "Epoch", position: "insideBottomRight", offset: -5, fontSize: 11 }}
          />
          <YAxis
            yAxisId="left"
            domain={[0.97, 1.001]}
            tick={{ fontSize: 10 }}
            tickFormatter={(v) => v.toFixed(4)}
            label={{ value: "Cosine Similarity", angle: -90, position: "insideLeft", fontSize: 11, dy: 40 }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 10 }}
            label={{ value: "L2 Distance", angle: 90, position: "insideRight", fontSize: 11, dy: -40 }}
          />
          <Tooltip
            contentStyle={{ fontSize: 11, borderRadius: 6, border: "1px solid #E2E8F0" }}
            formatter={(value: number, name: string) => {
              if (name === "cosine_similarity") return [value.toFixed(6), "Cosine 相似度"];
              if (name === "l2_distance") return [value.toFixed(1), "L2 距离"];
              return [value, name];
            }}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="cosine_similarity"
            stroke="var(--chart-line-1)"
            strokeWidth={1.5}
            dot={false}
            name="Cosine 相似度"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="l2_distance"
            stroke="#F97316"
            strokeWidth={1.5}
            dot={false}
            name="L2 距离"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
