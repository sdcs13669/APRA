import { useState, useEffect } from "react";
import type { DefenseMethod, AttackMethod } from "../types";
import { getTrajectoryCsvPath } from "../lib/data-paths";
import { parseCsv } from "../lib/csv";

interface TrajectoryRow {
  epoch: number;
  cosine_similarity: number;
  l2_distance: number;
  backdoor: number;
  main: number;
}

export function useTrajectoryData(defense: DefenseMethod, attack: AttackMethod) {
  const [data, setData] = useState<TrajectoryRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(getTrajectoryCsvPath(defense, attack))
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.text();
      })
      .then((text) => {
        const raw = parseCsv<Record<string, string>>(text);
        const parsed: TrajectoryRow[] = raw.map((row) => ({
          epoch: Number(row.epoch ?? row[""] ?? 0),
          cosine_similarity: Number(row.cosine_similarity ?? 0),
          l2_distance: Number(row.l2_distance ?? 0),
          backdoor: Number(row.backdoor ?? 0),
          main: Number(row.main ?? 0),
        }));
        setData(parsed);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [defense, attack]);

  return { data, loading, error };
}
