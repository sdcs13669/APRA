import { useState, useEffect } from "react";
import type { AccuracyRow, DefenseMethod, AttackMethod, DatasetType } from "../types";
import { getAccuracyCsvPath } from "../lib/data-paths";
import { parseCsv } from "../lib/csv";

export function useAccuracyData(defense: DefenseMethod, attack: AttackMethod, dataset: DatasetType) {
  const [data, setData] = useState<AccuracyRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(getAccuracyCsvPath(defense, attack, dataset))
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.text();
      })
      .then((text) => {
        const raw = parseCsv<Record<string, string>>(text);
        const parsed: AccuracyRow[] = raw.map((row) => ({
          epoch: Number(row.epoch ?? row.Epoch ?? row[""] ?? 0),
          test_acc: Number(row.main ?? row.test_acc ?? row["test acc"] ?? 0),
          bkd_acc: Number(row.backdoor ?? row.bkd_acc ?? row["bkd acc"] ?? 0),
          test_loss: Number(row.test_loss ?? row["test loss"] ?? 0),
          bkd_loss: Number(row.bkd_loss ?? row["bkd loss"] ?? 0),
          lr: row.lr ? Number(row.lr) : undefined,
        }));
        setData(parsed);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [defense, attack, dataset]);

  return { data, loading, error };
}
