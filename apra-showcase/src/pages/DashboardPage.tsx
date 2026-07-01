import { useState } from "react";
import type { DefenseMethod, AttackMethod } from "../types";
import { useSummaryData } from "../hooks/useSummaryData";
import ControlBar from "../components/dashboard/ControlBar";
import CombinedChart from "../components/dashboard/CombinedChart";
import RadarChart from "../components/dashboard/RadarChart";
import TrajectoryChart from "../components/dashboard/TrajectoryChart";

export default function DashboardPage() {
  const [defense, setDefense] = useState<DefenseMethod>("apra");
  const [attack, setAttack] = useState<AttackMethod>("a3fl");
  const { data: summary } = useSummaryData();

  const currentResult = summary?.[defense]?.[attack] ?? null;

  return (
    <div className="pt-16 bg-[#F8FAFC] min-h-screen">
      <ControlBar
        defense={defense}
        attack={attack}
        onDefenseChange={setDefense}
        onAttackChange={setAttack}
        asr={currentResult?.asr ?? null}
        accuracy={currentResult?.accuracy ?? null}
      />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CombinedChart selectedDefense={defense} selectedAttack={attack} />
          <RadarChart attack={attack} />
        </div>
        <div className="mt-6">
          <TrajectoryChart selectedDefense={defense} selectedAttack={attack} />
        </div>
      </div>
    </div>
  );
}
