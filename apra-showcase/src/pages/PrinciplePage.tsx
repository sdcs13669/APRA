import StageCard from "../components/principle/StageCard";
import ComparisonTable from "../components/principle/ComparisonTable";

const stages = [
  {
    stage: 1 as const,
    title: "APRA 总体算法流程",
    description: "从客户端训练到聚合防御的完整闭环",
    image: "/APRA 总体算法流程.png",
  },
  {
    stage: 2 as const,
    title: "多维特征提取与自适应 MAD 预过滤",
    description: "L2 范数 + NBD/NDIF 行为特征 → PCA 降维 → 鲁棒异常检测",
    image: "/多维特征提取与MAD过滤详图.png",
  },
  {
    stage: 3 as const,
    title: "层次聚类与可信簇选择",
    description: "Ward 凝聚聚类 + 轮廓系数自动选 K → 簇得分最大化",
    image: "/层次聚类与可信簇选择详图.png",
  },
  {
    stage: 4 as const,
    title: "信任加权与自适应裁剪",
    description: "孤立度 → Logit 变换 → 信任权重 → 裁剪因子 → 加权聚合",
    image: "/信任加权计算详图.png",
  },
];

export default function PrinciplePage() {
  return (
    <div className="pt-24 pb-16 bg-[#F8FAFC]">
      <div className="max-w-5xl mx-auto px-4">
        <h1
          className="text-3xl text-center mb-4 font-bold text-slate-800"
          style={{ fontFamily: "'Lexend', sans-serif" }}
        >
          技术原理
        </h1>
        <p className="text-center text-slate-500 mb-12 text-lg">
          APRA 四阶段渐进式防御流程
        </p>

        {stages.map((s) => (
          <StageCard
            key={s.stage}
            stage={s.stage}
            title={s.title}
            description={s.description}
            image={s.image}
          />
        ))}

        <ComparisonTable />
      </div>
    </div>
  );
}
