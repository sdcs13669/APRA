import { useState, useEffect, useRef, useCallback } from "react";
import { useApraTrace } from "../hooks/useApraTrace";
import { useAccuracyData } from "../hooks/useAccuracyData";
import PlaybackControls from "../components/replay/PlaybackControls";
import ClientMatrix from "../components/replay/ClientMatrix";
import RoundStats from "../components/replay/RoundStats";
import AccuracyTrend from "../components/replay/AccuracyTrend";

const SPEED_MAP: Record<number, number> = { 1: 500, 2: 250, 5: 100 };

export default function ReplayPage() {
  const { frames, loading, error } = useApraTrace();
  const { data: accuracyData } = useAccuracyData("apra", "a3fl");
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [currentRound, setCurrentRound] = useState(1);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const totalRounds = frames.length > 0 ? frames[frames.length - 1].roundSummary.epoch : 1;
  const currentFrame = frames.find((f) => f.roundSummary.epoch === currentRound) ?? frames[frames.length - 1];

  const advanceRound = useCallback(() => {
    setCurrentRound((prev) => {
      const next = prev + 1;
      if (next > totalRounds) {
        setPlaying(false);
        return prev;
      }
      return next;
    });
  }, [totalRounds]);

  useEffect(() => {
    if (playing && frames.length > 0) {
      timerRef.current = setInterval(advanceRound, SPEED_MAP[speed]);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [playing, speed, advanceRound, frames.length]);

  if (loading) {
    return (
      <div className="pt-24 h-screen flex items-center justify-center text-slate-500" style={{ backgroundColor: "#F8FAFC" }}>
        Loading replay data...
      </div>
    );
  }

  if (error) {
    return (
      <div className="pt-24 h-screen flex items-center justify-center text-red-600" style={{ backgroundColor: "#F8FAFC" }}>
        Error loading data: {error}
      </div>
    );
  }

  if (!currentFrame) {
    return (
      <div className="pt-24 h-screen flex items-center justify-center text-slate-500" style={{ backgroundColor: "#F8FAFC" }}>
        No replay data available
      </div>
    );
  }

  return (
    <div className="pt-16" style={{ backgroundColor: "#F8FAFC", minHeight: "100vh" }}>
      <PlaybackControls
        playing={playing}
        currentRound={currentRound}
        totalRounds={totalRounds}
        speed={speed}
        onTogglePlay={() => setPlaying(!playing)}
        onSeek={setCurrentRound}
        onSpeedChange={setSpeed}
      />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6">
          <ClientMatrix roundSummary={currentFrame.roundSummary} clientTraces={currentFrame.clientTraces} />
          <RoundStats roundSummary={currentFrame.roundSummary} />
        </div>
        <div className="mt-6">
          <AccuracyTrend accuracyData={accuracyData} currentRound={currentRound} />
        </div>
      </div>
    </div>
  );
}
