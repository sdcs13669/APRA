import { Server, User, ShieldAlert } from "lucide-react";

export default function ArchitectureDiagram() {
  return (
    <div className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6 mb-8 max-w-2xl mx-auto">
      <div className="relative w-full h-80">
        {/* Center server */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
          <div className="p-4 rounded-full border-2 border-blue-400 bg-blue-50">
            <Server className="w-10 h-10 text-blue-600" />
          </div>
          <span
            className="mt-2 text-xs text-blue-600"
            style={{ fontFamily: "'Lexend', sans-serif" }}
          >
            APRA 聚合服务器
          </span>
        </div>

        {/* Benign clients */}
        {[20, 50, 80].map((angle, i) => (
          <div
            key={`benign-${i}`}
            className="absolute flex flex-col items-center"
            style={{
              top: `${30 + Math.sin((angle * Math.PI) / 180) * 40}%`,
              left: `${15 + i * 25}%`,
            }}
          >
            <User className="w-6 h-6 text-green-600" />
            <span className="text-[10px] text-green-600 mt-1">Client {i + 1}</span>
          </div>
        ))}

        {/* Malicious clients */}
        {[30, 60].map((angle, i) => (
          <div
            key={`mal-${i}`}
            className="absolute flex flex-col items-center"
            style={{
              top: `${60 + Math.sin((angle * Math.PI) / 180) * 30}%`,
              left: `${20 + i * 30}%`,
            }}
          >
            <ShieldAlert className="w-6 h-6 text-red-600" />
            <span className="text-[10px] text-red-600 mt-1">Attacker {i}</span>
          </div>
        ))}

        {/* Legend */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 flex gap-6 text-xs text-slate-500">
          <span className="flex items-center gap-1">
            <span className="w-3 h-0.5 bg-green-600 inline-block" /> 良性更新
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-0.5 bg-red-600 inline-block" /> 后门更新
          </span>
        </div>
      </div>
    </div>
  );
}
