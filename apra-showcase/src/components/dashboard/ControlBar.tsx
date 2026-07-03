import type { DefenseMethod, AttackMethod, DatasetType } from "../../types";
import { DEFENSE_METHODS, ATTACK_METHODS, DATASETS, DEFENSE_LABELS, ATTACK_LABELS, DATASET_LABELS } from "../../types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";

interface ControlBarProps {
  defense: DefenseMethod;
  attack: AttackMethod;
  dataset: DatasetType;
  onDefenseChange: (d: DefenseMethod) => void;
  onAttackChange: (a: AttackMethod) => void;
  onDatasetChange: (d: DatasetType) => void;
  asr: number | null;
  accuracy: number | null;
}

export default function ControlBar({
  defense,
  attack,
  dataset,
  onDefenseChange,
  onAttackChange,
  onDatasetChange,
  asr,
  accuracy,
}: ControlBarProps) {
  return (
    <div className="sticky top-16 z-40 backdrop-blur-md bg-white/90 border-b border-[#E2E8F0] shadow-sm py-4 px-6">
      <div className="max-w-7xl mx-auto flex items-center gap-6 flex-wrap">
        <div>
          <label className="text-xs text-slate-500 block mb-1" style={{ fontFamily: "'Lexend', sans-serif" }}>数据集</label>
          <Select value={dataset} onValueChange={(v) => onDatasetChange(v as DatasetType)}>
            <SelectTrigger className="w-36 bg-white border-[#E2E8F0] text-sm text-slate-800">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-white border-[#E2E8F0]">
              {DATASETS.map((ds) => (
                <SelectItem key={ds} value={ds} className="text-sm text-slate-800">
                  {DATASET_LABELS[ds]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-xs text-slate-500 block mb-1" style={{ fontFamily: "'Lexend', sans-serif" }}>防御方法</label>
          <Select value={defense} onValueChange={(v) => onDefenseChange(v as DefenseMethod)}>
            <SelectTrigger className="w-40 bg-white border-[#E2E8F0] text-sm text-slate-800">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-white border-[#E2E8F0]">
              {DEFENSE_METHODS.map((d) => (
                <SelectItem key={d} value={d} className="text-sm text-slate-800">
                  {DEFENSE_LABELS[d]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-xs text-slate-500 block mb-1" style={{ fontFamily: "'Lexend', sans-serif" }}>攻击方法</label>
          <Select value={attack} onValueChange={(v) => onAttackChange(v as AttackMethod)}>
            <SelectTrigger className="w-40 bg-white border-[#E2E8F0] text-sm text-slate-800">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-white border-[#E2E8F0]">
              {ATTACK_METHODS.map((a) => (
                <SelectItem key={a} value={a} className="text-sm text-slate-800">
                  {ATTACK_LABELS[a]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="ml-auto flex gap-6">
          {asr !== null && (
            <div className="text-center">
              <p className="text-xs text-slate-500" style={{ fontFamily: "'Lexend', sans-serif" }}>ASR</p>
              <p className="text-xl font-bold text-red-600" style={{ fontFamily: "'Lexend', sans-serif" }}>
                {asr}%
              </p>
            </div>
          )}
          {accuracy !== null && (
            <div className="text-center">
              <p className="text-xs text-slate-500" style={{ fontFamily: "'Lexend', sans-serif" }}>准确率</p>
              <p className="text-xl font-bold text-green-600" style={{ fontFamily: "'Lexend', sans-serif" }}>
                {accuracy}%
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
