import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { 
  FileText, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  Upload, 
  Search, 
  ShieldCheck, 
  Database, 
  ArrowRight,
  Activity,
  Layers,
  Sparkles
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import api from "../api/client";

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<any[]>([]);
  const [recentAudits, setRecentAudits] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [docsRes, auditsRes, healthRes] = await Promise.all([
          api.get("/documents"),
          api.get("/audit?limit=6").catch(() => ({ data: [] })),
          api.get("/health").catch(() => ({ data: null }))
        ]);
        setDocuments(docsRes.data || []);
        setRecentAudits(auditsRes.data || []);
        setHealth(healthRes.data);
      } catch (err) {
        console.error("Dashboard data load error:", err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const pendingCount = documents.filter((d) => d.status === "UNDER_REVIEW").length;
  const approvedCount = documents.filter((d) => d.status === "APPROVED").length;
  const rejectedCount = documents.filter((d) => d.status === "REJECTED").length;
  const draftCount = documents.filter((d) => d.status === "DRAFT").length;

  const statusBadge = (status: string) => {
    switch (status) {
      case "APPROVED":
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200/80">Approved</span>;
      case "UNDER_REVIEW":
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200/80">Under Review</span>;
      case "REJECTED":
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200/80">Rejected</span>;
      case "ARCHIVED":
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200">Archived</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200/80">Draft</span>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-7">
      {/* Welcome & Quick Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Enterprise Workspace
            </h1>
            <span className="text-[10px] font-mono px-2 py-0.2 rounded-md bg-slate-100 text-slate-600 border border-slate-200 font-semibold">
              {user?.tenant_id}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Logged in as <span className="font-semibold text-slate-800">{user?.email}</span> • Active Scope: <span className="font-semibold text-indigo-600">{user?.permissions.join(", ")}</span>
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          {user?.role !== "VIEWER" && (
            <Link
              to="/documents?upload=true"
              className="inline-flex items-center px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl shadow-xs transition-all hover:shadow-sm"
            >
              <Upload className="w-3.5 h-3.5 mr-1.5" />
              Upload Document
            </Link>
          )}
          <Link
            to="/search"
            className="inline-flex items-center px-3.5 py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-xl border border-slate-200/80 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 mr-1.5 text-indigo-600" />
            AI RAG Search
          </Link>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Documents */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-card flex items-center justify-between hover:border-slate-300 transition-colors">
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Total In Scope</div>
            <div className="text-2xl font-bold text-slate-900 mt-0.5 tracking-tight">{documents.length}</div>
            <div className="text-[11px] text-slate-500 mt-1 flex items-center">
              <span className="font-semibold text-indigo-600 mr-1">{draftCount}</span> in Draft stage
            </div>
          </div>
          <div className="w-11 h-11 rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center shadow-2xs">
            <FileText className="w-5 h-5" />
          </div>
        </div>

        {/* Pending Review */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-card flex items-center justify-between hover:border-slate-300 transition-colors">
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Pending Review</div>
            <div className="text-2xl font-bold text-amber-600 mt-0.5 tracking-tight">{pendingCount}</div>
            <div className="text-[11px] text-slate-500 mt-1">Requires manager signoff</div>
          </div>
          <div className="w-11 h-11 rounded-xl bg-amber-50 border border-amber-100 text-amber-600 flex items-center justify-center shadow-2xs">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        {/* Approved */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-card flex items-center justify-between hover:border-slate-300 transition-colors">
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Approved</div>
            <div className="text-2xl font-bold text-emerald-600 mt-0.5 tracking-tight">{approvedCount}</div>
            <div className="text-[11px] text-slate-500 mt-1">Indexed in Vector RAG</div>
          </div>
          <div className="w-11 h-11 rounded-xl bg-emerald-50 border border-emerald-100 text-emerald-600 flex items-center justify-center shadow-2xs">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>

        {/* Rejected */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-card flex items-center justify-between hover:border-slate-300 transition-colors">
          <div>
            <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Rejected</div>
            <div className="text-2xl font-bold text-rose-600 mt-0.5 tracking-tight">{rejectedCount}</div>
            <div className="text-[11px] text-slate-500 mt-1">Returned for revision</div>
          </div>
          <div className="w-11 h-11 rounded-xl bg-rose-50 border border-rose-100 text-rose-600 flex items-center justify-center shadow-2xs">
            <XCircle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Polyglot Architecture & Health Overview */}
      <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-white shadow-card">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-5 border-b border-slate-800">
          <div>
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400/50 animate-pulse" />
              <span className="text-[10px] font-bold tracking-wider uppercase text-emerald-400">
                Multi-Model Infrastructure
              </span>
            </div>
            <h2 className="text-base font-bold mt-1 text-slate-100">
              Polyglot Storage & Zero-Leakage Vector Engine
            </h2>
          </div>
          <Link
            to="/audit"
            className="text-xs font-semibold px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white flex items-center transition-colors shadow-2xs"
          >
            <ShieldCheck className="w-3.5 h-3.5 mr-1.5" />
            Verify SHA-256 Chain
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 mt-5">
          <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/60">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">PostgreSQL</span>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-1.5 py-0.2 rounded border border-emerald-800/80">
                {health?.postgres || "connected"}
              </span>
            </div>
            <div className="text-xs font-medium text-slate-200 mt-1">ACID & Row-Level Security</div>
            <div className="text-[11px] text-slate-400 mt-1">Transactions, RBAC, and immutable audit logs</div>
          </div>

          <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/60">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">MongoDB</span>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-1.5 py-0.2 rounded border border-emerald-800/80">
                {health?.mongodb || "connected"}
              </span>
            </div>
            <div className="text-xs font-medium text-slate-200 mt-1">Document & Schema-Free Store</div>
            <div className="text-[11px] text-slate-400 mt-1">Dynamic metadata, extraction JSON, and tags</div>
          </div>

          <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/60">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">ChromaDB</span>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-1.5 py-0.2 rounded border border-emerald-800/80">
                active (HNSW)
              </span>
            </div>
            <div className="text-xs font-medium text-slate-200 mt-1">Dense Vector Embeddings</div>
            <div className="text-[11px] text-slate-400 mt-1">384-d cosine distance with pre-retrieval ACL mask</div>
          </div>
        </div>
      </div>

      {/* Main Grid: Recent Documents & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Documents Table (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
          <div className="p-4 sm:p-5 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-indigo-600" />
              <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">
                Authorized Documents In Scope
              </h3>
            </div>
            <Link to="/documents" className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center transition-colors">
              View All <ArrowRight className="w-3 h-3 ml-1" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-100 text-left text-xs">
              <thead className="bg-slate-50/75 text-slate-500 uppercase font-semibold">
                <tr>
                  <th className="px-5 py-3">Document Title</th>
                  <th className="px-5 py-3">Department</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {documents.slice(0, 5).map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-5 py-3.5">
                      <Link to={`/documents/${doc.id}`} className="font-semibold text-indigo-600 hover:text-indigo-800 block truncate max-w-[260px]">
                        {doc.title}
                      </Link>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">{doc.id}</div>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="capitalize px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-700 border border-slate-200/80">
                        {doc.department || "general"}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      {statusBadge(doc.status)}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="text-xs font-semibold text-slate-600 hover:text-indigo-600 transition-colors"
                      >
                        Inspect →
                      </Link>
                    </td>
                  </tr>
                ))}
                {documents.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-5 py-8 text-center text-slate-400">
                      No documents currently available in this scope.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Audit Log Feed (1 col) */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card p-5">
          <div className="flex items-center justify-between pb-3.5 border-b border-slate-100">
            <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center">
              <Activity className="w-3.5 h-3.5 mr-1.5 text-indigo-600" />
              Cryptographic Audit Stream
            </h3>
            <Link to="/audit" className="text-xs font-semibold text-indigo-600 hover:text-indigo-800">
              All
            </Link>
          </div>

          <div className="mt-3.5 space-y-2.5">
            {recentAudits.slice(0, 5).map((ev) => (
              <div key={ev.id} className="text-xs p-2.5 rounded-xl bg-slate-50/70 border border-slate-200/60 hover:bg-slate-50 transition-colors">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-800 text-[11px]">{ev.action}</span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <div className="text-slate-500 mt-1 flex items-center justify-between text-[11px]">
                  <span className="truncate max-w-[140px]">{ev.actor_email}</span>
                  {ev.document_id && <span className="font-mono text-indigo-600 font-semibold">{ev.document_id}</span>}
                </div>
                <div className="text-[9px] font-mono text-slate-400 truncate mt-1">
                  Hash: {ev.current_hash.slice(0, 16)}...
                </div>
              </div>
            ))}
            {recentAudits.length === 0 && (
              <div className="text-center py-6 text-slate-400 text-xs">
                No recent audit events
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

