import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-4 bg-[#F8FAFC]">
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1
          className="text-5xl md:text-6xl font-bold mb-6 leading-tight text-slate-800"
          style={{
            fontFamily: "'Lexend', sans-serif",
            background: "linear-gradient(135deg, #2563EB, #8B5CF6)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          让联邦学习
          <br />
          不再被后门挟持
        </h1>
        <p className="text-lg text-slate-500 mb-10 max-w-xl mx-auto">
          自适应渐进鲁棒聚合 · 全国大学生信息安全竞赛作品赛
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-all"
          >
            查看实验数据 <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/principle"
            className="inline-flex items-center gap-2 px-6 py-3 border border-blue-600 text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
          >
            了解技术原理 <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </motion.div>
    </section>
  );
}
