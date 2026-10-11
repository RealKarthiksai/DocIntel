import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { 
  FileText, 
  ArrowLeft, 
  CheckCircle2, 
  XCircle, 
  Archive, 
  Send, 
  ShieldCheck, 
  Clock, 
  Database,
  Trash2,
  AlertTriangle,
  Share2,
  X,
  Copy,
  Check,
  Layers,
  ChevronRight,
  GitPullRequest
} from "lucide-react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export const DocumentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [document, setDocument] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"workflow" | "metadata" | "audit">("workflow");
  const [isShareOpen, setIsShareOpen] = useState(false);
  const [granteeType, setGranteeType] = useState<"USER" | "ROLE" | "DEPARTMENT">("USER");
  const [granteeId, setGranteeId] = useState("");
  const [permissionLevel, setPermissionLevel] = useState("READ");
  const [sharing, setSharing] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  const isApprover = user?.role === "SUPER_ADMIN" || user?.role === "ADMIN" || user?.role === "MANAGER";
  const isDeleter = user?.role === "SUPER_ADMIN" || user?.role === "ADMIN" || (document && user?.id === document.created_by);

  const handleCopyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const auditActionBadge = (action: string) => {
    switch (action) {
      case "DOCUMENT_UPLOADED":
      case "DOCUMENT_INGESTED":
        return "bg-indigo-50 text-indigo-700 border-indigo-200/80";
      case "SUBMITTED_FOR_REVIEW":
        return "bg-amber-50 text-amber-700 border-amber-200/80";
      case "APPROVED":
        return "bg-emerald-50 text-emerald-700 border-emerald-200/80";
      case "REJECTED":
        return "bg-rose-50 text-rose-700 border-rose-200/80";
      case "ARCHIVED":
        return "bg-slate-100 text-slate-700 border-slate-200";
      case "DOCUMENT_ACCESS_GRANTED":
        return "bg-purple-50 text-purple-700 border-purple-200/80";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200";
    }
  };

  const loadDocument = async () => {
    try {
      setLoading(true);
      setActionError(null);
      const [docRes, histRes, auditRes] = await Promise.all([
        api.get(`/documents/${id}`),
        api.get(`/documents/${id}/history`).catch(() => ({ data: [] })),
        api.get(`/audit/${id}`).catch(() => ({ data: [] }))
      ]);
      setDocument(docRes.data);
      setHistory(histRes.data || []);
      setAuditLogs(auditRes.data || []);
    } catch (err: any) {
      setActionError(err.response?.data?.detail || "Failed to load document.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocument();
  }, [id]);

  const handleTransition = async (action: "submit" | "approve" | "reject" | "archive") => {
    setActionError(null);
    setActionSuccess(null);
    try {
      const res = await api.post(`/documents/${id}/${action}`, { comment: `Action triggered via UI by ${user?.email}` });
      setActionSuccess(res.data.message);
      await loadDocument();
    } catch (err: any) {
      setActionError(err.response?.data?.detail || `Failed to ${action} document.`);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this document from all stores? Cryptographic audit logs will preserve the event record.")) return;
    try {
      await api.delete(`/documents/${id}`);
      navigate("/documents");
    } catch (err: any) {
      setActionError(err.response?.data?.detail || "Delete failed.");
    }
  };

  const handleCopyJson = () => {
    if (document?.metadata) {
      navigator.clipboard.writeText(JSON.stringify(document.metadata, null, 2));
      setCopiedJson(true);
      setTimeout(() => setCopiedJson(false), 2000);
    }
  };

  const handleShareSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!granteeId.trim()) return;
    setSharing(true);
    setActionError(null);
    setActionSuccess(null);
    try {
      const formData = new FormData();
      formData.append("grantee_type", granteeType);
      formData.append("grantee_id", granteeId.trim());
      formData.append("permission_level", permissionLevel);
      await api.post(`/documents/${id}/share`, formData);
      setActionSuccess(`Access policy granted: ${granteeType} '${granteeId.trim()}' (${permissionLevel})!`);
      setIsShareOpen(false);
      setGranteeId("");
      await loadDocument();
    } catch (err: any) {
      setActionError(err.response?.data?.detail || "Failed to grant access policy.");
    } finally {
      setSharing(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-20 text-center text-slate-400 text-xs">
        Loading document records across polyglot stores...
      </div>
    );
  }

  if (!document) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center space-y-3">
        <div className="text-rose-600 font-bold text-sm">Document Not Accessible</div>
        <p className="text-slate-500 text-xs">{actionError || "You may lack departmental or ACL permissions to inspect this record."}</p>
        <Link to="/documents" className="inline-flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-800">
          ← Return to Document Repository
        </Link>
      </div>
    );
  }

  const steps = [
    { label: "DRAFT", desc: "Ingestion & Hash Check" },
    { label: "UNDER_REVIEW", desc: "Dual-Custody Inspection" },
    { label: document.status === "REJECTED" ? "REJECTED" : "APPROVED", desc: document.status === "REJECTED" ? "Revision Required" : "Ready for Vector Query" },
    { label: "ARCHIVED", desc: "Long-term Storage" }
  ];

  const getStepIndex = (status: string) => {
    switch (status) {
      case "DRAFT": return 0;
      case "UNDER_REVIEW": return 1;
      case "APPROVED":
      case "REJECTED": return 2;
      case "ARCHIVED": return 3;
      default: return 0;
    }
  };

  const currentStep = getStepIndex(document.status);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Back Link */}
      <div>
        <Link 
          to="/documents" 
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors w-fit group"
        >
          <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" />
          <span>Back to Documents</span>
        </Link>
      </div>

        {/* Action Notification */}
        {actionSuccess && (
          <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between animate-fade-in">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{actionSuccess}</span>
            </div>
            <button onClick={() => setActionSuccess(null)} className="text-xs font-bold text-emerald-600 hover:text-emerald-800">✕</button>
          </div>
        )}
        {actionError && (
          <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between animate-fade-in">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{actionError}</span>
            </div>
            <button onClick={() => setActionError(null)} className="text-xs font-bold text-rose-600 hover:text-rose-800">✕</button>
          </div>
        )}

        {/* Title & Metadata Card */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">{document.title}</h1>
              <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${
                document.status === "APPROVED" ? "bg-emerald-50 text-emerald-700 border-emerald-200/80" :
                document.status === "UNDER_REVIEW" ? "bg-amber-50 text-amber-700 border-amber-200/80" :
                document.status === "REJECTED" ? "bg-rose-50 text-rose-700 border-rose-200/80" :
                document.status === "ARCHIVED" ? "bg-slate-100 text-slate-700 border-slate-200" :
                "bg-indigo-50 text-indigo-700 border-indigo-200/80"
              }`}>
                {document.status}
              </span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono mt-1.5 flex items-center gap-2 flex-wrap">
              <span>ID: <strong className="text-slate-600 font-bold">{document.id}</strong></span>
              <span>•</span>
              <span>Tenant: <strong className="text-slate-600">{document.tenant_id}</strong></span>
              <span>•</span>
              <span>Created by: <strong className="text-slate-600">{document.creator_email || document.created_by}</strong></span>
            </div>
          </div>

        {/* Workflow Actions Toolbar */}
        <div className="flex flex-wrap items-center gap-2">
          {document.status === "DRAFT" && user?.role !== "VIEWER" && (
            <button
              onClick={() => handleTransition("submit")}
              className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-xs transition-all hover:shadow-sm"
            >
              <Send className="w-3.5 h-3.5 mr-1.5" />
              Submit for Review
            </button>
          )}

          {document.status === "UNDER_REVIEW" && isApprover && (
            <>
              <button
                onClick={() => handleTransition("approve")}
                className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs transition-all hover:shadow-sm"
              >
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                Approve
              </button>
              <button
                onClick={() => handleTransition("reject")}
                className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200/80 transition-colors"
              >
                <XCircle className="w-3.5 h-3.5 mr-1.5" />
                Reject
              </button>
            </>
          )}

          {document.status === "APPROVED" && isApprover && (
            <button
              onClick={() => handleTransition("archive")}
              className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-900 text-white shadow-xs transition-colors"
            >
              <Archive className="w-3.5 h-3.5 mr-1.5" />
              Archive
            </button>
          )}

          {(isDeleter || user?.id === document.created_by) && (
            <button
              onClick={() => setIsShareOpen(true)}
              className="inline-flex items-center px-3 py-2 rounded-xl text-xs font-semibold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200/80 transition-colors"
            >
              <Share2 className="w-3.5 h-3.5 mr-1.5" />
              Share (ACL)
            </button>
          )}

          {isDeleter && (
            <button
              onClick={handleDelete}
              title="Delete Document"
              className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors border border-transparent hover:border-rose-100"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Modern Segmented Tab Bar */}
      <div className="flex items-center justify-start border-b border-slate-200/80 pb-3">
        <div className="inline-flex items-center p-1 bg-slate-100/90 rounded-xl border border-slate-200/80 shadow-2xs">
          <button
            onClick={() => setActiveTab("workflow")}
            className={`inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all focus:outline-none ${
              activeTab === "workflow"
                ? "bg-white text-indigo-700 shadow-xs font-bold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
            }`}
          >
            <GitPullRequest className="w-3.5 h-3.5" />
            <span>Workflow & Timeline</span>
          </button>
          <button
            onClick={() => setActiveTab("metadata")}
            className={`inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all focus:outline-none ${
              activeTab === "metadata"
                ? "bg-white text-indigo-700 shadow-xs font-bold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span>Polyglot Metadata</span>
          </button>
          <button
            onClick={() => setActiveTab("audit")}
            className={`inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all focus:outline-none ${
              activeTab === "audit"
                ? "bg-white text-indigo-700 shadow-xs font-bold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Cryptographic Chain</span>
            <span className="px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[10px] font-mono font-bold">
              {auditLogs.length}
            </span>
          </button>
        </div>
      </div>

      {/* Tab 1: Workflow Lifecycle */}
      {activeTab === "workflow" && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-card">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Finite State Machine Progression
              </h3>
              <span className="text-[11px] font-medium text-slate-500">
                Stage {currentStep + 1} of {steps.length}
              </span>
            </div>

            {/* Clean Minimal Horizontal Stepper */}
            <div className="relative">
              {/* Connector line behind steps */}
              <div className="hidden sm:block absolute top-4 left-6 right-6 h-0.5 bg-slate-100 -z-0" />
              
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 relative z-10">
                {steps.map((st, idx) => {
                  const isPast = idx < currentStep;
                  const isCurrent = idx === currentStep;

                  return (
                    <div key={st.label} className="flex flex-col items-start sm:items-center text-left sm:text-center group">
                      {/* Step Circle Indicator */}
                      <div className="flex items-center space-x-3 sm:space-x-0 sm:flex-col sm:items-center w-full">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all shrink-0 ${
                            isCurrent
                              ? "bg-indigo-600 text-white ring-4 ring-indigo-50 shadow-sm"
                              : isPast
                              ? "bg-emerald-600 text-white shadow-xs"
                              : "bg-white text-slate-400 border-2 border-slate-200"
                          }`}
                        >
                          {isPast ? (
                            <CheckCircle2 className="w-4 h-4" />
                          ) : (
                            <span>{idx + 1}</span>
                          )}
                        </div>

                        <div className="mt-0 sm:mt-2.5">
                          <div className={`text-xs font-bold tracking-tight ${
                            isCurrent ? "text-indigo-700" : isPast ? "text-slate-800" : "text-slate-400"
                          }`}>
                            {st.label}
                          </div>
                          <div className="text-[11px] text-slate-500 mt-0.5 leading-snug max-w-[160px]">
                            {st.desc}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Workflow Transition History Table */}
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
            <div className="p-4 border-b border-slate-100 font-bold text-xs uppercase tracking-wider text-slate-700">
              State Transition Audit Records
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-100 text-left text-xs">
                <thead className="bg-slate-50/75 text-slate-500 uppercase font-semibold">
                  <tr>
                    <th className="px-5 py-3">Transition</th>
                    <th className="px-5 py-3">Actor</th>
                    <th className="px-5 py-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {history.map((h) => (
                    <tr key={h.id}>
                      <td className="px-5 py-3 font-semibold">
                        <span className="px-2 py-0.5 rounded text-[11px] bg-slate-100 border border-slate-200 font-mono">{h.from_state}</span>
                        <span className="mx-2 text-slate-300">→</span>
                        <span className="px-2 py-0.5 rounded text-[11px] bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono font-bold">{h.to_state}</span>
                      </td>
                      <td className="px-5 py-3 text-slate-600">{h.actor_email || `User #${h.actor_id}`}</td>
                      <td className="px-5 py-3 text-slate-400 font-mono text-[11px]">{new Date(h.timestamp).toLocaleString()}</td>
                    </tr>
                  ))}
                  {history.length === 0 && (
                    <tr>
                      <td colSpan={3} className="px-5 py-6 text-center text-slate-400">
                        No workflow transitions recorded yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Polyglot Metadata */}
      {activeTab === "metadata" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-card space-y-3.5">
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-900 border-b border-slate-100 pb-2.5 flex items-center">
              <Database className="w-3.5 h-3.5 mr-2 text-indigo-600" />
              PostgreSQL Relational Fields
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-50"><span className="text-slate-400">ID:</span><span className="font-mono font-bold text-slate-800">{document.id}</span></div>
              <div className="flex justify-between py-1 border-b border-slate-50"><span className="text-slate-400">MongoDB Link:</span><span className="font-mono text-slate-600">{document.mongo_document_id}</span></div>
              <div className="flex justify-between py-1 border-b border-slate-50"><span className="text-slate-400">Status:</span><span className="font-bold">{document.status}</span></div>
              <div className="flex justify-between py-1 border-b border-slate-50"><span className="text-slate-400">Tenant Isolation:</span><span className="font-mono text-slate-600">{document.tenant_id}</span></div>
              <div className="flex justify-between py-1 border-b border-slate-50"><span className="text-slate-400">Created At:</span><span className="font-mono text-[11px]">{new Date(document.created_at).toLocaleString()}</span></div>
              <div className="flex justify-between py-1"><span className="text-slate-400">Updated At:</span><span className="font-mono text-[11px]">{new Date(document.updated_at).toLocaleString()}</span></div>
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-card space-y-3.5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <h3 className="font-bold text-xs uppercase tracking-wider text-slate-900 flex items-center">
                <Database className="w-3.5 h-3.5 mr-2 text-emerald-600" />
                MongoDB Flexible Metadata
              </h3>
              <button
                onClick={handleCopyJson}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center space-x-1"
              >
                {copiedJson ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-emerald-600">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy JSON</span>
                  </>
                )}
              </button>
            </div>
            <pre className="bg-slate-900 text-slate-100 p-4 rounded-xl text-xs font-mono overflow-x-auto max-h-80 shadow-inner">
              {JSON.stringify(document.metadata, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Tab 3: Cryptographic Audit Trail */}
      {activeTab === "audit" && (
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-900">
              Document Audit Chain ({auditLogs.length} Events)
            </h3>
            <span className="text-[11px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              ✓ SHA-256 Chained
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-100 text-left text-xs">
              <thead className="bg-slate-50/75 text-slate-500 uppercase font-semibold">
                <tr>
                  <th className="px-5 py-3">Event Action</th>
                  <th className="px-5 py-3">Actor</th>
                  <th className="px-5 py-3">Timestamp</th>
                  <th className="px-5 py-3">Previous Hash → Current Hash</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-5 py-3">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${auditActionBadge(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <div className="flex items-center space-x-2">
                        <div className="w-5 h-5 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-[10px] font-bold text-slate-700">
                          {log.actor_email ? log.actor_email.charAt(0).toUpperCase() : "U"}
                        </div>
                        <span className="text-slate-800 font-medium">{log.actor_email}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-slate-500 font-mono text-[11px]">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-5 py-3 font-mono text-[11px]">
                      <div className="flex items-center space-x-2">
                        <span title={log.previous_hash} className="text-slate-400">
                          {log.previous_hash.slice(0, 8)}...
                        </span>
                        <span className="text-slate-300">→</span>
                        <div className="inline-flex items-center space-x-1.5 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-md">
                          <span title={log.current_hash} className="text-slate-900 font-semibold">
                            {log.current_hash.slice(0, 10)}...
                          </span>
                          <button
                            type="button"
                            onClick={() => handleCopyHash(log.current_hash)}
                            title="Copy full SHA-256 block hash"
                            className="p-0.5 text-slate-400 hover:text-indigo-600 transition-colors"
                          >
                            {copiedHash === log.current_hash ? (
                              <Check className="w-3 h-3 text-emerald-600" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </button>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Share Document ACL Modal */}
      {isShareOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-modal border border-slate-200 space-y-4 animate-fade-in">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-slate-900 flex items-center">
                <Share2 className="w-4 h-4 mr-2 text-indigo-600" />
                Grant Granular Access Policy (ACL)
              </h3>
              <button onClick={() => setIsShareOpen(false)} className="text-slate-400 hover:text-slate-600 p-1">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleShareSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Grantee Type
                </label>
                <select
                  value={granteeType}
                  onChange={(e) => setGranteeType(e.target.value as any)}
                  className="w-full px-3 py-2 bg-slate-50/50 border border-slate-300/80 rounded-xl text-xs focus:ring-2 focus:ring-indigo-500 focus:bg-white focus:outline-none"
                >
                  <option value="USER">Specific User (User ID)</option>
                  <option value="ROLE">Specific Role (e.g. EMPLOYEE)</option>
                  <option value="DEPARTMENT">Specific Department (e.g. engineering)</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Grantee Identifier *
                </label>
                <input
                  type="text"
                  required
                  placeholder={granteeType === "USER" ? "e.g. 5" : granteeType === "ROLE" ? "e.g. EMPLOYEE" : "e.g. engineering"}
                  value={granteeId}
                  onChange={(e) => setGranteeId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50/50 border border-slate-300/80 rounded-xl text-xs focus:ring-2 focus:ring-indigo-500 focus:bg-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Permission Level
                </label>
                <select
                  value={permissionLevel}
                  onChange={(e) => setPermissionLevel(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50/50 border border-slate-300/80 rounded-xl text-xs focus:ring-2 focus:ring-indigo-500 focus:bg-white focus:outline-none"
                >
                  <option value="READ">READ (Query via RAG & View Document)</option>
                  <option value="WRITE">WRITE (Edit & Transition)</option>
                </select>
              </div>

              <div className="pt-3 flex justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsShareOpen(false)}
                  className="px-3 py-1.5 border border-slate-300/80 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={sharing}
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-all disabled:opacity-50"
                >
                  {sharing ? "Granting..." : "Grant Access"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

