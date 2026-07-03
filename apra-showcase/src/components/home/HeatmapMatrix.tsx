import { useState } from "react";
import { motion } from "framer-motion";
import { useSummaryData } from "../../hooks/useSummaryData";
import { DEFENSE_METHODS, ATTACK_METHODS, DATASETS, DEFENSE_LABELS, ATTACK_LABELS, DATASET_LABELS } from "../../types";
import type { DefenseMethod, DatasetType } from "../../types";

export default function HeatmapMatrix() {
  const [dataset, setDataset] = useState<DatasetType>("cifar10");
  const { data, loading } = useSummaryData(dataset);

  return (
    <section className="max-w-6xl mx-auto px-4 pb-24">
      <div className="flex items-center justify-center gap-4 mb-10">
        <h2
          className="text-2xl text-center tracking-wider text-slate-800"
          style={{ fontFamily: "'Lexend', sans-serif" }}
        >
          防御方法 × 攻击方法 · ASR 热力图
        </h2>
        <div className="flex gap-1 bg-slate-100 rounded-lg p-0.5">
          {DATASETS.map((ds) => (
            <button
              key={ds}
              onClick={() => setDataset(ds)}
              className={`px-3 py-1 text-xs rounded-md font-medium transition-colors ${
                dataset === ds
                  ? "bg-white text-slate-800 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {DATASET_LABELS[ds]}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-500">Loading...</div>
      ) : !data ? null : (
        (() => {
          const asrValues: number[] = [];
          ATTACK_METHODS.forEach((attack) => {
            DEFENSE_METHODS.forEach((defense) => {
              const val = data[defense]?.[attack]?.asr;
              if (val !== undefined) asrValues.push(val);
            });
          });
          const maxAsr = Math.max(...asrValues);
          const minAsr = Math.min(...asrValues);

          // Find best defense per attack column
          const bestPerAttack: Record<string, DefenseMethod> = {};
          ATTACK_METHODS.forEach((attack) => {
            let best: DefenseMethod | null = null;
            let bestVal = Infinity;
            DEFENSE_METHODS.forEach((defense) => {
              const val = data[defense]?.[attack]?.asr;
              if (val !== undefined && val < bestVal) {
                bestVal = val;
                best = defense;
              }
            });
            if (best) bestPerAttack[attack] = best;
          });

          function getColor(asr: number): string {
            const ratio = maxAsr === minAsr ? 0.5 : (asr - minAsr) / (maxAsr - minAsr);
            if (ratio < 0.33) return "#22C55E";
            if (ratio < 0.66) return "#F59E0B";
            return "#DC2626";
          }

          return (
            <div className="overflow-x-auto bg-white shadow-sm border border-[#E2E8F0] rounded-lg">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#E2E8F0]">
                    <th className="p-3 text-left text-sm text-slate-700 font-medium">防御 \ 攻击</th>
                    {ATTACK_METHODS.map((attack) => (
                      <th key={attack} className="p-3 text-center text-sm text-slate-700 font-medium">
                        {ATTACK_LABELS[attack]}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {DEFENSE_METHODS.map((defense) => (
                    <tr key={defense} className={`${defense === "apra" ? "bg-blue-50" : ""} border-b border-[#E2E8F0] last:border-b-0`}>
                      <td
                        className={`p-3 text-sm font-bold ${
                          defense === "apra" ? "text-blue-600" : "text-slate-700"
                        }`}
                        style={{ fontFamily: "'Lexend', sans-serif" }}
                      >
                        {DEFENSE_LABELS[defense]}
                      </td>
                      {ATTACK_METHODS.map((attack) => {
                        const result = data[defense]?.[attack];
                        const asr = result?.asr;
                        const isBest = bestPerAttack[attack] === defense;
                        return (
                          <td key={attack} className="p-3 text-center">
                            {asr !== undefined ? (
                              <motion.div
                                initial={{ scale: 0 }}
                                whileInView={{ scale: 1 }}
                                viewport={{ once: true }}
                                className={`inline-block w-full max-w-[100px] py-2 rounded text-xs font-bold cursor-default relative ${
                                  isBest ? "ring-2 ring-amber-400 shadow-md shadow-amber-200/50" : ""
                                }`}
                                style={{
                                  backgroundColor: getColor(asr),
                                  color: asr > 50 ? "#fff" : "#1E293B",
                                }}
                                title={`${DEFENSE_LABELS[defense]} × ${ATTACK_LABELS[attack]}\nASR: ${asr}%\nAccuracy: ${result?.accuracy}%${isBest ? "\n⭐ 该攻击类型最优防御" : ""}`}
                              >
                                {asr}%
                                {isBest && (
                                  <span className="absolute -top-1.5 -right-1.5 text-[10px] leading-none">
                                    👑
                                  </span>
                                )}
                              </motion.div>
                            ) : (
                              <span className="text-slate-400">—</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        })()
      )}
      <p className="text-center text-xs text-slate-500 mt-4">
        颜色越深 → ASR 越高（防御效果越差）· 悬停查看详情
      </p>
    </section>
  );
}
