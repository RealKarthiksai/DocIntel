import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShieldCheck, ArrowRight, Lock, Mail, FileText, CheckCircle2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid credentials. Please verify your email and password.");
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = async (userEmail: string, userPass: string) => {
    setEmail(userEmail);
    setPassword(userPass);
    setError(null);
    setLoading(true);
    try {
      await login(userEmail, userPass);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Quick login failed.");
    } finally {
      setLoading(false);
    }
  };

  const demoPersonas = [
    {
      role: "SUPER_ADMIN",
      title: "Super Admin",
      email: "superadmin@example.com",
      pass: "SuperAdminPass123!",
      badge: "Global Root",
      badgeColor: "bg-rose-50 text-rose-700 border-rose-200",
      desc: "Multi-tenant root & system configuration"
    },
    {
      role: "ADMIN",
      title: "System Admin",
      email: "admin@example.com",
      pass: "AdminPass123!",
      badge: "Full Access",
      badgeColor: "bg-purple-50 text-purple-700 border-purple-200",
      desc: "All documents, audit chain, and user management"
    },
    {
      role: "MANAGER",
      title: "Finance Manager",
      email: "finance_manager@example.com",
      pass: "FinManagerPass123!",
      badge: "Approval Rights",
      badgeColor: "bg-blue-50 text-blue-700 border-blue-200",
      desc: "Dual-custody document review & approval"
    },
    {
      role: "EMPLOYEE",
      title: "Finance Employee",
      email: "finance_emp@example.com",
      pass: "FinEmpPass123!",
      badge: "Standard User",
      badgeColor: "bg-emerald-50 text-emerald-700 border-emerald-200",
      desc: "Document ingestion & submit for review"
    },
    {
      role: "VIEWER",
      title: "Auditor / Viewer",
      email: "viewer@example.com",
      pass: "ViewerPass123!",
      badge: "Read Only",
      badgeColor: "bg-slate-100 text-slate-700 border-slate-200",
      desc: "Read-only inspection without write or mutate rights"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="mx-auto w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-700 to-violet-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25 mb-4">
          <FileText className="w-6 h-6" />
        </div>
        <div className="flex items-center justify-center space-x-2">
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">
            DocIntel Platform
          </h2>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
            Enterprise
          </span>
        </div>
        <p className="mt-1.5 text-xs text-slate-500">
          Cryptographic Audit & Multi-Model Document Intelligence
        </p>
      </div>

      <div className="mt-7 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-modal border border-slate-200/90 rounded-2xl sm:px-8 space-y-6">
          {error && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start space-x-2 animate-fade-in">
              <span className="font-bold shrink-0">Error:</span>
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleLogin}>
            <div>
              <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                Corporate Email
              </label>
              <div className="relative rounded-xl">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="block w-full pl-9 pr-3 py-2.5 bg-slate-50/50 border border-slate-300/80 rounded-xl text-xs placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                Password
              </label>
              <div className="relative rounded-xl">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="block w-full pl-9 pr-3 py-2.5 bg-slate-50/50 border border-slate-300/80 rounded-xl text-xs placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center items-center py-2.5 px-4 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 shadow-sm transition-all disabled:opacity-50"
            >
              {loading ? "Authenticating Session..." : "Sign In to Enterprise Workspace"}
              <ArrowRight className="ml-2 w-3.5 h-3.5" />
            </button>
          </form>

          {/* Quick Demo Switcher */}
          <div className="pt-4 border-t border-slate-100">
            <div className="flex items-center justify-between mb-2.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                1-Click Demo Personas
              </span>
              <span className="text-[10px] font-mono text-indigo-600 font-semibold">
                Instant Session
              </span>
            </div>

            <div className="space-y-1.5">
              {demoPersonas.map((p) => (
                <button
                  key={p.role}
                  type="button"
                  onClick={() => quickLogin(p.email, p.pass)}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl border border-slate-200/70 bg-slate-50/60 hover:bg-indigo-50/40 hover:border-indigo-200/80 text-left transition-all group"
                >
                  <div className="min-w-0 pr-2">
                    <div className="flex items-center space-x-1.5">
                      <span className="text-xs font-bold text-slate-900 group-hover:text-indigo-700 transition-colors">
                        {p.title}
                      </span>
                      <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded border ${p.badgeColor}`}>
                        {p.badge}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-500 truncate mt-0.5">
                      {p.email} • <span className="text-slate-400">{p.desc}</span>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-300 group-hover:text-indigo-600 shrink-0 transition-colors" />
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="text-center mt-5 text-[11px] text-slate-400">
          Protected by Polyglot Access Control • SHA-256 Chained Audits
        </div>
      </div>
    </div>
  );
};
