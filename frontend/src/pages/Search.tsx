import React, { useState } from "react";
import { Link } from "react-router-dom";
import { 
  Search as SearchIcon, 
  Sparkles, 
  ShieldCheck, 
  FileText, 
  AlertCircle, 
  Send, 
  CheckCircle2, 
  Lock, 
  ArrowRight, 
  HelpCircle,
  Copy,
  Check
} from "lucide-react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export const Search: React.FC = () => {
  const { user } = useAuth();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [copiedAnswer, setCopiedAnswer] = useState(false);

  const suggestedQueries = [
    {
      title: "Vendor Agreements & SLAs",
      prompt: "What are the standard termination clauses and SLA commitments in vendor contracts?",
      description: "Extracts termination conditions, liability caps, and uptime commitments from vendor agreements.",
      category: "contracts",
      badgeColor: "bg-purple-50 text-purple-700 border-purple-200/80"
    },
    {
      title: "Corporate Financial Analysis",
      prompt: "Summarize the key revenue targets, operating expenses, and quarterly budget figures.",
      description: "Aggregates revenue forecasts, expense allocations, and balance sheet indicators.",
      category: "finance",
      badgeColor: "bg-blue-50 text-blue-700 border-blue-200/80"
    },
    {
      title: "Human Resources & Workplace Policy",
      prompt: "What is the hybrid remote work policy and how many days can employees work from home?",
      description: "Queries company handbooks on remote eligibility, core working hours, and benefits.",
      category: "hr & policy",
      badgeColor: "bg-emerald-50 text-emerald-700 border-emerald-200/80"
    },
    {
      title: "Engineering & SRE Protocols",
      prompt: "What is the severity-1 incident escalation procedure and response protocol?",
      description: "Surfaces on-call escalation paths, recovery procedures, and post-mortem workflows.",
      category: "engineering",
      badgeColor: "bg-indigo-50 text-indigo-700 border-indigo-200/80"
    },
  ];

  const handleSearch = async (queryText?: string) => {
    const q = queryText || query;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const res = await api.post("/rag/query", { query: q, top_k: 4 });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Search query failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyAnswer = () => {
    if (result?.answer) {
      navigator.clipboard.writeText(result.answer);
      setCopiedAnswer(true);
      setTimeout(() => setCopiedAnswer(false), 2000);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-7">
      {/* Header & Access-Aware Scope Badge */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center">
            <Sparkles className="w-5 h-5 text-indigo-600 mr-2" />
            Enterprise Knowledge Search
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Grounded AI search across authorized contracts, policies, and operational documents
          </p>
        </div>

        {/* Security Scope Indicator */}
        <div className="p-3 bg-slate-50/70 rounded-xl border border-slate-200/80 text-xs shrink-0">
          <div className="flex items-center space-x-1.5 font-bold text-slate-800 text-[11px]">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Active Retrieval Scope:</span>
          </div>
          <div className="mt-1 text-slate-600 text-[11px]">
            Role: <span className="font-semibold text-indigo-600">{user?.role}</span>
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-0.5">
            Tenant: {user?.tenant_id} (Isolated)
          </div>
        </div>
      </div>

      {/* Search Input Bar */}
      <div className="bg-white p-3 rounded-2xl border border-slate-200/80 shadow-card">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex items-center gap-2.5"
        >
          <div className="relative flex-1">
            <SearchIcon className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question grounded in enterprise documents..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50/50 border border-slate-300/80 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all placeholder-slate-400"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow-xs transition-all hover:shadow-sm disabled:opacity-50 shrink-0"
          >
            {loading ? "Searching..." : "Search"}
            <Send className="w-3.5 h-3.5 ml-1.5" />
          </button>
        </form>
      </div>

      {/* Suggested Enterprise Queries */}
      <div className="space-y-3">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center">
          <HelpCircle className="w-3.5 h-3.5 mr-1" />
          Suggested Enterprise Queries
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {suggestedQueries.map((tp, idx) => (
            <div
              key={idx}
              onClick={() => {
                setQuery(tp.prompt);
                handleSearch(tp.prompt);
              }}
              className="p-4 rounded-xl border border-slate-200/80 bg-white hover:border-indigo-300 hover:bg-indigo-50/10 cursor-pointer transition-all shadow-card hover:shadow-card-hover space-y-1.5 group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">
                  {tp.title}
                </span>
                <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded border uppercase ${tp.badgeColor}`}>
                  {tp.category}
                </span>
              </div>
              <div className="text-xs text-indigo-700 font-medium">"{tp.prompt}"</div>
              <div className="text-[11px] text-slate-400 leading-relaxed">{tp.description}</div>
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs animate-fade-in">
          {error}
        </div>
      )}

      {/* RAG Results Display */}
      {result && (
        <div className="space-y-6 animate-fade-in">
          {/* Grounded Answer Card */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3.5">
              <div className="flex items-center space-x-2">
                <div className="w-7 h-7 rounded-lg bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">
                  Synthesized Grounded Answer
                </h3>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                  result.sources.length > 0 
                    ? "bg-emerald-50 text-emerald-700 border-emerald-200/80"
                    : "bg-slate-100 text-slate-600 border border-slate-200"
                }`}>
                  {result.sources.length > 0 ? `${result.sources.length} Sources Cited` : "0 Authorized Sources Found"}
                </span>
                <button
                  onClick={handleCopyAnswer}
                  className="text-xs text-slate-500 hover:text-slate-800 flex items-center space-x-1"
                  title="Copy answer"
                >
                  {copiedAnswer ? (
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>

            <p className="text-slate-800 text-xs leading-relaxed whitespace-pre-line bg-slate-50/60 p-4 rounded-xl border border-slate-100">
              {result.answer}
            </p>

            {/* Zero-Leakage Audit Badge */}
            <div className="text-[11px] text-slate-500 flex items-center justify-between pt-1">
              <span className="truncate max-w-sm">Query: "{result.query}"</span>
              <span className="font-mono text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-semibold shrink-0">
                ✓ Enforced Scope: [{result.user_department_scope.join(", ")}]
              </span>
            </div>
          </div>

          {/* Source Citations */}
          {result.sources.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center">
                <FileText className="w-3.5 h-3.5 mr-1 text-indigo-600" />
                Verifiable Source Citations ({result.sources.length})
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {result.sources.map((src: any, idx: number) => (
                  <div key={idx} className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-card hover:border-slate-300 transition-colors space-y-2.5">
                    <div className="flex items-start justify-between">
                      <div>
                        <Link
                          to={`/documents/${src.document_id}`}
                          className="font-bold text-xs text-indigo-600 hover:text-indigo-800 block truncate max-w-[220px]"
                        >
                          {src.document_title}
                        </Link>
                        <div className="text-[10px] text-slate-400 font-mono mt-0.5">ID: {src.document_id}</div>
                      </div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200/80">
                        Page {src.page}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-500 pt-2 border-t border-slate-100">
                      <span className="capitalize">Dept: {src.department}</span>
                      <span className="capitalize px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 font-medium">
                        {src.classification}
                      </span>
                      {src.relevance_score && (
                        <span className="font-mono font-bold text-emerald-600">
                          Match: {Math.round(src.relevance_score * 100)}%
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

