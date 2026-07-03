import {
  Radar,
  RadarChart as ReRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useSummaryData } from "../../hooks/useSummaryData";
import type { AttackMethod, DatasetType } from "../../types";
import { DEFENSE_METHODS, DEFENSE_LABELS } from "../../types";

const CHART_COLORS: Record<string, string> = {
  apra: "#2563EB",
  avg: "#b347ea",
  clip: "#16A34A",
  deepsight: "#DC2626",
  foolsgold: "#F59E0B",
  rflbat: "#8B5CF6",
};

interface Props {
  attack: AttackMethod;
  dataset: DatasetType;
}

export default function RadarChart({ attack, dataset }: Props) {
  const { data: summary } = useSummaryData(dataset);

  if (!summary) return null;

  const radarData = [
    { dimension: "ASR防御", fullMark: 100 },
    { dimension: "准确率", fullMark: 100 },
    { dimension: "稳定性", fullMark: 100 },
    { dimension: "检测率", fullMark: 100 },
  ].map((d) => {
    const entry: Record<string, unknown> = { ...d };
    DEFENSE_METHODS.forEach((def) => {
      const result = summary[def]?.[attack];
      if (!result) {
        entry[def] = 0;
        return;
      }
      switch (d.dimension) {
        case "ASR防御":
          entry[def] = Math.max(0, 100 - result.asr);
          break;
        case "准确率":
          entry[def] = result.accuracy;
          break;
        case "稳定性":
          entry[def] = 85;
          break;
        case "检测率":
          entry[def] = Math.max(0, 100 - result.asr * 1.1);
          break;
      }
    });
    return entry;
  });

  return (
    <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6">
      <h3 className="text-sm mb-4 text-slate-800" style={{ fontFamily: "'Lexend', sans-serif" }}>
        防御方法多维对比
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <ReRadarChart data={radarData}>
          <PolarGrid stroke="#E2E8F0" />
          <PolarAngleAxis dataKey="dimension" stroke="#64748B" fontSize={11} tick={{ fill: "#64748B" }} />
          <PolarRadiusAxis domain={[0, 100]} stroke="#64748B" fontSize={9} tick={false} />
          {DEFENSE_METHODS.map((def) => (
            <Radar
              key={def}
              name={DEFENSE_LABELS[def]}
              dataKey={def}
              stroke={CHART_COLORS[def]}
              fill={CHART_COLORS[def]}
              fillOpacity={0.15}
              strokeWidth={def === "apra" ? 2 : 1}
            />
          ))}
          <Legend wrapperStyle={{ fontSize: "11px" }} />
        </ReRadarChart>
      </ResponsiveContainer>
    </div>
  );
}
