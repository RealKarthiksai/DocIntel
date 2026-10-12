import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  ShieldCheck, 
  ArrowRight, 
  Lock, 
  Mail, 
  FileText, 
  CheckCircle2, 
  Eye, 
  EyeOff, 
  Crown, 
  UserCheck, 
  Upload, 
  Sparkles,
  Layers,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

interface PersonaConfig {
  id: string;
  role: string;
  title: string;
  badge: string;
  badgeColor: string;
  cardBorder: string;
  iconBg: string;
  iconColor: string;
  Icon: React.ElementType;
  description: string;
  email: string;
  pass: string;
  canDo: string[];
}

export const Login: React.FC = () => {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("AdminPass123!");
  const [showPassword, setShowPassword] = useState(false);
  const [showManualForm, setShowManualForm] = useState(false);
  const [selectedPersona, setSelectedPersona] = useState<string>("admin");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  // 4 Crystal-Clear, Simplified Roles
  const personas: PersonaConfig[] = [
    {
      id: "admin",
      role: "ADMIN",
      title: "Administrator",
      badge: "Full Control",
      badgeColor: "bg-purple-100 text-purple-800 border-purple-200",
      cardBorder: "hover:border-purple-300 focus:border-purple-500",
      iconBg: "bg-purple-50 text-purple-600 border-purple-200",
      iconColor: "text-purple-600",
      Icon: Crown,
      description: "Manage users, inspect SHA-256 audit logs, and oversee all departments.",
      email: "admin@example.com",
      pass: "AdminPass123!",
      canDo: ["Manage users & permissions", "Full audit ledger access", "Approve & delete any document"]
    },
    {
      id: "manager",
      role: "MANAGER",
      title: "Manager / Approver",
      badge: "Review & Sign",
      badgeColor: "bg-blue-100 text-blue-800 border-blue-200",
      cardBorder: "hover:border-blue-300 focus:border-blue-500",
      iconBg: "bg-blue-50 text-blue-600 border-blue-200",
      iconColor: "text-blue-600",
      Icon: UserCheck,
      description: "Review submitted files, trigger workflow state transitions, and approve drafts.",
      email: "finance_manager@example.com",
      pass: "FinManagerPass123!",
      canDo: ["Review team submissions", "Approve or reject drafts", "Manage department workflows"]
    },
    {
      id: "contributor",
      role: "EMPLOYEE",
      title: "Team Contributor",
      badge: "Upload & Edit",
      badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-200",
      cardBorder: "hover:border-emerald-300 focus:border-emerald-500",
      iconBg: "bg-emerald-50 text-emerald-600 border-emerald-200",
      iconColor: "text-emerald-600",
      Icon: Upload,
      description: "Upload PDFs & Word files, edit metadata, and search with RAG AI.",
      email: "finance_emp@example.com",
      pass: "FinEmpPass123!",
      canDo: ["Upload PDF / DOCX documents", "Submit drafts for approval", "Chat with RAG semantic AI"]
    },
    {
      id: "viewer",
      role: "VIEWER",
      title: "Auditor / Viewer",
      badge: "Read Only",
      badgeColor: "bg-amber-100 text-amber-800 border-amber-200",
      cardBorder: "hover:border-amber-300 focus:border-amber-500",
      iconBg: "bg-amber-50 text-amber-600 border-amber-200",
      iconColor: "text-amber-600",
      Icon: ShieldCheck,
      description: "Read-only access to view published files and verify audit integrity.",
      email: "viewer@example.com",
      pass: "ViewerPass123!",
      canDo: ["Search & read documents", "Verify tamper-proof hashes", "Zero write or delete risk"]
    }
  ];

  const handlePersonaSelect = (p: PersonaConfig) => {
    setSelectedPersona(p.id);
    setEmail(p.email);
    setPassword(p.pass);
    setError(null);
  };

  const executeLogin = async (loginEmail: string, loginPass: string) => {
    setError(null);
    setLoading(true);
    try {
      await login(loginEmail, loginPass);
      navigate("/dashboard");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        "Authentication failed. Please verify the credentials or try a 1-click persona."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeLogin(email, password);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col lg:flex-row text-slate-100 selection:bg-indigo-500 selection:text-white">
      {/* LEFT PANEL: Enterprise Branding & Architecture Overview */}
      <div className="lg:w-5/12 bg-gradient-to-b from-slate-900 via-slate-950 to-slate-900 border-b lg:border-b-0 lg:border-r border-slate-800/80 p-8 sm:p-12 flex flex-col justify-between relative overflow-hidden">
        {/* Ambient Glow Effects */}
        <div className="absolute -top-32 -left-32 w-80 h-80 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10">
          {/* Logo & Platform Tag */}
          <div className="flex items-center space-x-3 mb-8">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-indigo-500 via-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25 ring-1 ring-white/20">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-white">DocIntel</span>
                <span className="text-[10px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                  Enterprise
                </span>
              </div>
              <p className="text-xs text-slate-400">Cryptographic Document Intelligence</p>
            </div>
          </div>

          {/* Heading */}
          <div className="space-y-3 mb-10">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white leading-tight">
              Simplified Role-Based Access with Cryptographic Integrity.
            </h1>
            <p className="text-sm text-slate-400 leading-relaxed">
              Every role has clear, isolated boundaries. Select a persona to test the platform with built-in permission guardrails.
            </p>
          </div>

          {/* 4 Roles Overview Guide */}
          <div className="space-y-3">
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
              <span>How The 4 Roles Work</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 hover:border-purple-500/40 transition-colors">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 rounded-full bg-purple-400" />
                  <span className="text-xs font-bold text-slate-200">Admin</span>
                </div>
                <p className="text-[11px] text-slate-400">Full system oversight, user management & audit inspection.</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 hover:border-blue-500/40 transition-colors">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 rounded-full bg-blue-400" />
                  <span className="text-xs font-bold text-slate-200">Manager</span>
                </div>
                <p className="text-[11px] text-slate-400">Reviews submissions and approves or rejects drafts.</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 hover:border-emerald-500/40 transition-colors">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span className="text-xs font-bold text-slate-200">Contributor</span>
                </div>
                <p className="text-[11px] text-slate-400">Uploads files, edits drafts & queries RAG AI.</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800/80 hover:border-amber-500/40 transition-colors">
                <div className="flex items-center space-x-2 mb-1">
                  <div className="w-2 h-2 rounded-full bg-amber-400" />
                  <span className="text-xs font-bold text-slate-200">Auditor</span>
                </div>
                <p className="text-[11px] text-slate-400">Read-only inspection to verify compliance & hashes.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Guarantee */}
        <div className="mt-10 pt-6 border-t border-slate-800/70 relative z-10 flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>SHA-256 Tamper-Evident Ledger</span>
          </div>
          <span className="font-mono text-slate-400">v1.0 • Enterprise</span>
        </div>
      </div>

      {/* RIGHT PANEL: Sleek Interactive Login Canvas */}
      <div className="lg:w-7/12 bg-slate-50 flex items-center justify-center p-6 sm:p-10 lg:p-12 text-slate-900">
        <div className="w-full max-w-xl space-y-6">
          {/* Header */}
          <div className="text-center sm:text-left">
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              <span>Instant 1-Click Persona Demo</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Sign In to Enterprise Workspace
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-1">
              Select any role tile below to immediately test its permissions, or enter custom credentials.
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start space-x-2.5 animate-fade-in shadow-sm">
              <span className="font-bold shrink-0">Sign In Error:</span>
              <span className="leading-relaxed">{error}</span>
            </div>
          )}

          {/* 1-CLICK PERSONA TILES (2x2 GRID) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Choose a Role to Test
              </span>
              <span className="text-[11px] text-indigo-600 font-semibold">
                Click any tile to launch
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {personas.map((p) => {
                const IconComponent = p.Icon;
                const isSelected = selectedPersona === p.id;

                return (
                  <div
                    key={p.id}
                    onClick={() => handlePersonaSelect(p)}
                    className={`p-4 rounded-2xl border text-left transition-all cursor-pointer relative group flex flex-col justify-between ${
                      isSelected
                        ? "bg-white border-indigo-600 shadow-md ring-2 ring-indigo-500/20"
                        : "bg-white/80 border-slate-200 hover:border-slate-300 hover:bg-white hover:shadow-sm"
                    }`}
                  >
                    <div>
                      {/* Card Header: Icon & Badge */}
                      <div className="flex items-center justify-between mb-2.5">
                        <div className={`w-9 h-9 rounded-xl flex items-center justify-center border ${p.iconBg}`}>
                          <IconComponent className="w-5 h-5" />
                        </div>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${p.badgeColor}`}>
                          {p.badge}
                        </span>
                      </div>

                      {/* Title & Description */}
                      <h3 className="text-sm font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                        {p.title}
                      </h3>
                      <p className="text-[11px] text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                        {p.description}
                      </p>

                      {/* Capabilities pill list */}
                      <div className="mt-3 space-y-1">
                        {p.canDo.slice(0, 2).map((item, idx) => (
                          <div key={idx} className="flex items-center text-[10px] text-slate-600 space-x-1.5">
                            <CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />
                            <span className="truncate">{item}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Instant Login Action Button */}
                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                      <span className="text-[10px] font-mono text-slate-400 truncate max-w-[120px]">
                        {p.email}
                      </span>
                      <button
                        type="button"
                        disabled={loading}
                        onClick={(e) => {
                          e.stopPropagation();
                          handlePersonaSelect(p);
                          executeLogin(p.email, p.pass);
                        }}
                        className={`inline-flex items-center px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all ${
                          isSelected
                            ? "bg-indigo-600 text-white hover:bg-indigo-700 shadow-xs"
                            : "bg-slate-100 text-slate-700 hover:bg-indigo-50 hover:text-indigo-700"
                        }`}
                      >
                        <span>Launch</span>
                        <ArrowRight className="w-3 h-3 ml-1" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ACTIVE SELECTED PERSONA ACTION BAR */}
          {selectedPersona && (
            <div className="p-4 rounded-2xl bg-white border border-indigo-200/80 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center space-x-3 text-left w-full sm:w-auto">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600 shrink-0">
                  <CheckCircle2 className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-slate-900">
                      Selected: {personas.find(p => p.id === selectedPersona)?.title}
                    </span>
                    <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                      {email}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Ready to sign in with complete role permissions
                  </p>
                </div>
              </div>

              <button
                type="button"
                disabled={loading}
                onClick={() => executeLogin(email, password)}
                className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold tracking-wide shadow-md shadow-indigo-600/20 hover:shadow-indigo-600/30 flex items-center justify-center transition-all disabled:opacity-50 shrink-0"
              >
                {loading ? "Signing in..." : "Launch This Persona"}
                <ArrowRight className="w-3.5 h-3.5 ml-2" />
              </button>
            </div>
          )}

          {/* COLLAPSIBLE MANUAL LOGIN FORM */}
          <div className="pt-2">
            <button
              type="button"
              onClick={() => setShowManualForm(!showManualForm)}
              className="w-full flex items-center justify-between py-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors border-t border-slate-200/80"
            >
              <span>Or sign in with custom corporate credentials</span>
              {showManualForm ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showManualForm && (
              <form onSubmit={handleSubmit} className="mt-3 space-y-3.5 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm animate-fade-in">
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Corporate Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                      <Mail className="h-4 w-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="name@example.com"
                      className="block w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                      <Lock className="h-4 w-4" />
                    </div>
                    <input
                      type={showPassword ? "text" : "password"}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="block w-full pl-9 pr-10 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center items-center py-2.5 px-4 rounded-xl text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 shadow-sm transition-all disabled:opacity-50"
                >
                  {loading ? "Authenticating Session..." : "Sign In with Credentials"}
                  <ArrowRight className="ml-2 w-3.5 h-3.5" />
                </button>
              </form>
            )}
          </div>

          {/* Compliance & Security Tag */}
          <div className="text-center text-[11px] text-slate-400">
            Protected by Dual-Custody Approval • RBAC Guardrails • SHA-256 Ledger
          </div>
        </div>
      </div>
    </div>
  );
};
