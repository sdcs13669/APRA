import { useState, useEffect } from "react";
import type { SummaryData, DatasetType } from "../types";
import { getSummaryPath } from "../lib/data-paths";

export function useSummaryData(dataset: DatasetType) {
  const [data, setData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(getSummaryPath(dataset))
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json) => {
        setData(json as SummaryData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [dataset]);

  return { data, loading, error };
}
