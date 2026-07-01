const methods = [
  { name: "APRA", strategy: "多维特征+MAD+聚类+信任加权", complexity: "高", robustness: "★★★★★", adaptivity: "自适应" },
  { name: "FedAvg", strategy: "简单平均", complexity: "低", robustness: "★", adaptivity: "无" },
  { name: "Clip", strategy: "范数裁剪", complexity: "低", robustness: "★★", adaptivity: "固定阈值" },
  { name: "DeepSight", strategy: "NDIF/NBD+DBSCAN聚类", complexity: "中", robustness: "★★★", adaptivity: "无" },
  { name: "FoolsGold", strategy: "历史余弦相似度", complexity: "中", robustness: "★★★", adaptivity: "无" },
  { name: "RFLBAT", strategy: "PCA+KMeans+欧氏距离", complexity: "中", robustness: "★★★", adaptivity: "无" },
];

export default function ComparisonTable() {
  return (
    <div className="mt-12">
      <h3
        className="text-xl text-center mb-6 font-semibold text-slate-800"
        style={{ fontFamily: "'Lexend', sans-serif" }}
      >
        防御方法对比
      </h3>
      <div className="overflow-x-auto bg-white shadow-sm border border-[#E2E8F0] rounded-lg">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[#E2E8F0]">
              <th className="p-3 text-left text-xs text-slate-500 uppercase tracking-wider">方法</th>
              <th className="p-3 text-left text-xs text-slate-500 uppercase tracking-wider">核心策略</th>
              <th className="p-3 text-left text-xs text-slate-500 uppercase tracking-wider">复杂度</th>
              <th className="p-3 text-left text-xs text-slate-500 uppercase tracking-wider">鲁棒性</th>
              <th className="p-3 text-left text-xs text-slate-500 uppercase tracking-wider">适应性</th>
            </tr>
          </thead>
          <tbody>
            {methods.map((m) => (
              <tr
                key={m.name}
                className={`border-b border-[#E2E8F0] ${
                  m.name === "APRA" ? "bg-blue-50" : ""
                }`}
              >
                <td
                  className={`p-3 font-bold ${m.name === "APRA" ? "text-blue-600" : "text-slate-600"}`}
                  style={{ fontFamily: "'Lexend', sans-serif" }}
                >
                  {m.name}
                </td>
                <td className="p-3 text-slate-600">{m.strategy}</td>
                <td className="p-3 text-slate-600">{m.complexity}</td>
                <td className="p-3 text-slate-600">{m.robustness}</td>
                <td className="p-3 text-slate-600">{m.adaptivity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
