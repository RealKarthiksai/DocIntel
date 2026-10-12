import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  FileText, 
  LayoutDashboard, 
  GitPullRequest, 
  ShieldCheck, 
  Search, 
  LogOut, 
  User as UserIcon,
  Sparkles
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import api from "../api/client";
import { NotificationCenter } from "./NotificationCenter";

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await api.get("/health");
        setHealth(res.data);
      } catch (err) {
        setHealth({ status: "error" });
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { label: "Documents", path: "/documents", icon: FileText },
    { label: "Workflow", path: "/workflow", icon: GitPullRequest },
    { label: "Audit Ledger", path: "/audit", icon: ShieldCheck },
    { label: "AI Search", path: "/search", icon: Sparkles },
  ];

  const roleColors: Record<string, string> = {
    SUPER_ADMIN: "bg-purple-50 text-purple-700 border-purple-200",
    ADMIN: "bg-purple-50 text-purple-700 border-purple-200",
    MANAGER: "bg-blue-50 text-blue-700 border-blue-200",
    EMPLOYEE: "bg-emerald-50 text-emerald-700 border-emerald-200",
    VIEWER: "bg-amber-50 text-amber-700 border-amber-200",
  };

  const roleDisplayNames: Record<string, string> = {
    SUPER_ADMIN: "Admin",
    ADMIN: "Admin",
    MANAGER: "Manager",
    EMPLOYEE: "Contributor",
    VIEWER: "Auditor",
  };

  return (
    <header className="glass-header border-b border-slate-200/80 sticky top-0 z-40 transition-all duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo & Navigation */}
          <div className="flex items-center space-x-6 min-w-0">
            <Link to="/dashboard" className="flex items-center space-x-2.5 group shrink-0">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-700 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform">
                <FileText className="w-4 h-4" />
              </div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base text-slate-900 tracking-tight">DocIntel</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-50/80 text-indigo-700 border border-indigo-200/60 shadow-2xs">
                  Enterprise
                </span>
              </div>
            </Link>

            <nav className="hidden md:flex items-center space-x-1 shrink-0">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname.startsWith(item.path);
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                      isActive
                        ? "bg-indigo-50 text-indigo-700 font-semibold"
                        : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                    }`}
                  >
                    <Icon className={`w-3.5 h-3.5 mr-1.5 shrink-0 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right Controls: Telemetry, Notifications & User */}
          <div className="flex items-center space-x-3 shrink-0">
            {/* System Health Telemetry */}
            <div className="hidden xl:flex items-center space-x-2 text-[11px] px-2.5 py-1 rounded-full bg-slate-50 border border-slate-200/80 whitespace-nowrap">
              <span className={`w-2 h-2 rounded-full ${
                health?.status === "healthy" ? "bg-emerald-500 shadow-xs shadow-emerald-400/50 animate-pulse" : "bg-amber-500"
              }`} />
              <span className="text-slate-600 font-medium">
                {health?.status === "healthy" ? "Polyglot Engine Live" : "Connecting..."}
              </span>
            </div>

            {/* Notification Center */}
            {user && <NotificationCenter />}

            {user ? (
              <div className="flex items-center pl-2 border-l border-slate-200/60">
                <div className="flex items-center space-x-2.5 bg-slate-50/90 hover:bg-slate-100/80 border border-slate-200/80 rounded-xl px-2.5 py-1 transition-all shadow-2xs">
                  <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-xs font-bold shrink-0 shadow-2xs">
                    {user.email.slice(0, 1).toUpperCase()}
                  </div>
                  <div className="text-left hidden sm:block">
                    <div className="text-xs font-semibold text-slate-800 leading-tight max-w-[130px] truncate" title={user.email}>
                      {user.email}
                    </div>
                    <div className="flex items-center space-x-1 mt-0.5">
                      <span className={`text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded border leading-none ${
                        roleColors[user.role] || "bg-slate-100 text-slate-700 border-slate-200"
                      }`}>
                        {roleDisplayNames[user.role] || user.role}
                      </span>
                      <span className="text-[9px] font-mono text-slate-500 bg-white px-1.5 py-0.5 rounded border border-slate-200/80 leading-none">
                        {user.tenant_id}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={logout}
                    title="Sign Out"
                    className="p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors ml-0.5"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center px-3.5 py-1.5 text-xs font-semibold rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 shadow-xs transition-colors"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
