import { useState, useEffect } from "react";
import type { AttackMethod, DatasetType } from "../types";
import { DEFENSE_METHODS } from "../types";
import { getAccuracyCsvPath } from "../lib/data-paths";
import { parseCsv } from "../lib/csv";

export type ComparisonMode =
  | { type: "accuracy"; attack: AttackMethod }
  | { type: "asr"; attack: AttackMethod };

export interface MultiLinePoint {
  epoch: number;
  [key: string]: number;
}

export function useMultiAccuracyData(mode: ComparisonMode, dataset: DatasetType) {
  const [data, setData] = useState<MultiLinePoint[]>([]);
  const [series, setSeries] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const attack = mode.attack;

    const combos = DEFENSE_METHODS.map((d) => ({
      defense: d,
      attack,
      label: d,
    }));

    setSeries(combos.map((c) => c.label));
    setLoading(true);

    Promise.all(
      combos.map(({ defense, attack: atk, label }) =>
        fetch(getAccuracyCsvPath(defense, atk, dataset))
          .then((res) => {
            if (!res.ok) return { label, rows: [] };
            return res.text().then((text) => ({ label, rows: parseCsv<Record<string, string>>(text) }));
          })
          .catch(() => ({ label, rows: [] as Record<string, string>[] }))
      )
    ).then((results) => {
      if (cancelled) return;

      const epochMap = new Map<number, MultiLinePoint>();

      for (const { label, rows } of results) {
        for (const row of rows) {
          const epoch = Number(row.epoch ?? row[""] ?? 0);
          const value =
            mode.type === "accuracy"
              ? Number(row.main ?? row.test_acc ?? 0)
              : Number(row.backdoor ?? row.bkd_acc ?? 0);
          if (!epochMap.has(epoch)) {
            epochMap.set(epoch, { epoch });
          }
          epochMap.get(epoch)![label] = value;
        }
      }

      const merged = Array.from(epochMap.values()).sort((a, b) => a.epoch - b.epoch);
      setData(merged);
      setLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, [mode.type, mode.attack, dataset]);

  return { data, series, loading };
}
