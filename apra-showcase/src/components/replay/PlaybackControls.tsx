import { Play, Pause } from "lucide-react";

interface Props {
  playing: boolean;
  currentRound: number;
  totalRounds: number;
  speed: number;
  onTogglePlay: () => void;
  onSeek: (round: number) => void;
  onSpeedChange: (speed: number) => void;
}

export default function PlaybackControls({
  playing,
  currentRound,
  totalRounds,
  speed,
  onTogglePlay,
  onSeek,
  onSpeedChange,
}: Props) {
  const progress = totalRounds > 1 ? ((currentRound - 1) / (totalRounds - 1)) * 100 : 0;

  return (
    <div className="sticky top-16 z-40 backdrop-blur-md bg-white/90 border-b border-[#E2E8F0] shadow-sm py-3 px-6">
      <div className="max-w-7xl mx-auto flex items-center gap-6">
        <button
          onClick={onTogglePlay}
          className="w-12 h-12 rounded-full border-2 border-blue-600 flex items-center justify-center hover:bg-blue-50 transition-all"
        >
          {playing ? (
            <Pause className="w-5 h-5 text-blue-600" />
          ) : (
            <Play className="w-5 h-5 text-blue-600 ml-0.5" />
          )}
        </button>

        <div className="flex-1">
          <input
            type="range"
            min={1}
            max={totalRounds}
            value={currentRound}
            onChange={(e) => onSeek(Number(e.target.value))}
            className="w-full h-2 rounded-full appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #2563EB ${progress}%, #CBD5E1 ${progress}%)`,
            }}
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span style={{ fontFamily: "'Lexend', sans-serif" }}>Round {currentRound}</span>
            <span style={{ fontFamily: "'Lexend', sans-serif" }}>Round {totalRounds}</span>
          </div>
        </div>

        <div className="flex gap-2">
          {[1, 2, 5].map((s) => (
            <button
              key={s}
              onClick={() => onSpeedChange(s)}
              className={`px-3 py-1 rounded text-xs border transition-all ${
                speed === s
                  ? "border-blue-600 text-blue-600 bg-blue-50"
                  : "border-[#E2E8F0] text-slate-500 hover:border-slate-400"
              }`}
              style={{ fontFamily: "'Lexend', sans-serif" }}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
