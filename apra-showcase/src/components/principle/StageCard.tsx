import { motion } from "framer-motion";
import { Layers, Filter, GitBranch, Shield } from "lucide-react";

const stageIcons = [Layers, Filter, GitBranch, Shield];

interface StageCardProps {
  stage: 1 | 2 | 3 | 4;
  title: string;
  description: string;
  image: string;
}

export default function StageCard({ stage, title, description, image }: StageCardProps) {
  const Icon = stageIcons[stage - 1];

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: stage * 0.1 }}
      className="bg-white shadow-sm border border-[#E2E8F0] rounded-lg p-6 mb-8"
    >
      <div className="flex items-center gap-4 mb-4">
        <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-blue-50 text-blue-600">
          <span className="text-lg font-bold" style={{ fontFamily: "'Lexend', sans-serif" }}>
            {String(stage).padStart(2, "0")}
          </span>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-slate-800" style={{ fontFamily: "'Lexend', sans-serif" }}>
            {title}
          </h3>
          <p className="text-sm text-slate-500">{description}</p>
        </div>
        <Icon className="w-5 h-5 text-blue-400 ml-auto" />
      </div>
      <img
        src={image}
        alt={title}
        className="w-full rounded border border-[#E2E8F0]"
        loading="lazy"
      />
    </motion.div>
  );
}
