import { NavLink } from "react-router-dom";
import { Shield } from "lucide-react";

const links = [
  { to: "/", label: "首页" },
  { to: "/principle", label: "技术原理" },
  { to: "/dashboard", label: "实验看板" },
  { to: "/replay", label: "训练回放" },
];

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-[#E2E8F0] shadow-sm">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <NavLink to="/" className="flex items-center gap-3 group">
          <Shield className="w-7 h-7 text-blue-600" />
          <span
            className="text-xl tracking-wider text-blue-600 transition-all"
            style={{ fontFamily: "'Lexend', sans-serif" }}
          >
            APRA
          </span>
        </NavLink>

        <div className="flex gap-8">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) =>
                `text-sm tracking-wide pb-1 border-b-2 transition-all ${
                  isActive
                    ? "text-blue-600 border-blue-600"
                    : "text-slate-500 border-transparent hover:text-slate-800"
                }`
              }
              style={{ fontFamily: "'Lexend', sans-serif" }}
            >
              {link.label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
}
