import { motion } from "framer-motion";
import { useSpringNumber } from "../../hooks/useSpringNumber";

interface Metric {
  label: string;
  value: number;
  suffix: string;
  detail: string;
  borderColor: string;
}

const metrics: Metric[] = [
  {
    label: "ASR 降低",
    value: 84,
    suffix: "%",
    detail: "89.3% → 14.2%",
    borderColor: "#2563EB",
  },
  {
    label: "主任务精度",
    value: 907,
    suffix: "",
    detail: "90.7% 保持可用",
    borderColor: "#8B5CF6",
  },
  {
    label: "抵御攻击",
    value: 5,
    suffix: " 种",
    detail: "A3FL / DOBA / ModelReplace / Neurotoxin / ReBA",
    borderColor: "#22C55E",
  },
];

function MetricCard({ metric }: { metric: Metric }) {
  const displayValue = useSpringNumber(metric.value);

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
      className="relative p-6 rounded-lg bg-white shadow-sm border border-[#E2E8F0]"
      style={{
        borderLeftColor: metric.borderColor,
        borderLeftWidth: 4,
      }}
    >
      <p className="text-sm text-slate-500 mb-3">{metric.label}</p>
      <motion.span
        className="text-4xl font-bold block mb-2 text-slate-800"
        style={{ fontFamily: "'Lexend', sans-serif" }}
      >
        {displayValue}
        <span className="text-2xl">{metric.suffix}</span>
      </motion.span>
      <p className="text-xs text-slate-500">{metric.detail}</p>
    </motion.div>
  );
}

export default function MetricsCards() {
  return (
    <section className="max-w-5xl mx-auto px-4 -mt-20 relative z-10 pb-20">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {metrics.map((metric) => (
          <MetricCard key={metric.label} metric={metric} />
        ))}
      </div>
    </section>
  );
}
