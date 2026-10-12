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
  Search,
  Sparkles,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Printer,
  Tag,
  Building,
  User,
  Calendar,
  Layers,
  Lock,
  Globe,
  HelpCircle
} from "lucide-react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

interface DocumentContentData {
  document_id: string;
  title: string;
  department: string;
  classification: string;
  status: string;
  total_pages: number;
  total_chunks: number;
  total_words: number;
  total_chars: number;
  summary: string;
  pages: Array<{
    page: number;
    text: string;
    word_count: number;
  }>;
  chunks: Array<{
    chunk_id: string;
    page: number;
    chunk_seq: number;
    text: string;
    word_count: number;
  }>;
  full_text: string;
}

export const DocumentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [document, setDocument] = useState<any>(null);
  const [docContent, setDocContent] = useState<DocumentContentData | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [contentLoading, setContentLoading] = useState(true);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  
  // Default tab is "reader" so users can immediately view the document!
  const [activeTab, setActiveTab] = useState<"reader" | "workflow" | "properties" | "audit">("reader");
  
  // Reader state
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [viewMode, setViewMode] = useState<"single" | "continuous">("continuous");
  const [searchQuery, setSearchQuery] = useState("");
  const [copiedText, setCopiedText] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  // Share ACL modal state
  const [isShareOpen, setIsShareOpen] = useState(false);
  const [granteeType, setGranteeType] = useState<"USER" | "ROLE" | "DEPARTMENT">("USER");
  const [granteeId, setGranteeId] = useState("");
  const [permissionLevel, setPermissionLevel] = useState("READ");
  const [sharing, setSharing] = useState(false);

  const isApprover = user?.role === "SUPER_ADMIN" || user?.role === "ADMIN" || user?.role === "MANAGER";
  const isDeleter = user?.role === "SUPER_ADMIN" || user?.role === "ADMIN" || (document && user?.id === document.created_by);

  const handleCopyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const handleCopyFullText = () => {
    if (docContent?.full_text) {
      navigator.clipboard.writeText(docContent.full_text);
      setCopiedText(true);
      setTimeout(() => setCopiedText(false), 2000);
    }
  };

  const handleCopyJson = () => {
    if (document?.metadata) {
      navigator.clipboard.writeText(JSON.stringify(document.metadata, null, 2));
      setCopiedJson(true);
      setTimeout(() => setCopiedJson(false), 2000);
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

  const loadContent = async () => {
    try {
      setContentLoading(true);
      const contentRes = await api.get(`/documents/${id}/content`);
      setDocContent(contentRes.data);
    } catch (err) {
      // Fallback if content endpoint has issues
      console.warn("Could not fetch document content:", err);
    } finally {
      setContentLoading(false);
    }
  };

  useEffect(() => {
    loadDocument();
    loadContent();
  }, [id]);

  const handleTransition = async (action: "submit" | "approve" | "reject" | "archive") => {
    setActionError(null);
    setActionSuccess(null);
    try {
      const res = await api.post(`/documents/${id}/${action}`, { 
        comment: `Action triggered via UI by ${user?.email}` 
      });
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
      <div className="max-w-5xl mx-auto px-4 py-24 text-center">
        <div className="w-10 h-10 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-slate-500 text-xs font-semibold">Opening document...</p>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="max-w-xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-12 h-12 bg-rose-50 text-rose-600 rounded-2xl flex items-center justify-center mx-auto border border-rose-200">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h2 className="text-slate-900 font-bold text-base">Document Not Accessible</h2>
        <p className="text-slate-500 text-xs leading-relaxed">
          {actionError || "You may lack departmental clearance or ACL permissions to inspect this record."}
        </p>
        <Link 
          to="/documents" 
          className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-xs"
        >
          <ArrowLeft className="w-3.5 h-3.5 mr-1.5" />
          Return to Documents
        </Link>
      </div>
    );
  }

  // Friendly status labels & explanations
  const statusConfig: Record<string, { label: string; badge: string; desc: string }> = {
    DRAFT: {
      label: "Draft",
      badge: "bg-indigo-50 text-indigo-700 border-indigo-200",
      desc: "Document is drafted and private to your department. Ready to submit for manager review."
    },
    UNDER_REVIEW: {
      label: "Under Review",
      badge: "bg-amber-50 text-amber-800 border-amber-200",
      desc: "Submitted for approval. Department managers must inspect and approve or reject."
    },
    APPROVED: {
      label: "Approved & Live",
      badge: "bg-emerald-50 text-emerald-800 border-emerald-200",
      desc: "Officially certified, cryptographically recorded, and active in AI search."
    },
    REJECTED: {
      label: "Rejected",
      badge: "bg-rose-50 text-rose-800 border-rose-200",
      desc: "Document requires revisions before re-submitting for approval."
    },
    ARCHIVED: {
      label: "Archived",
      badge: "bg-slate-100 text-slate-700 border-slate-200",
      desc: "Permanently stored in archival storage. Retained for compliance."
    }
  };

  const currentStatusInfo = statusConfig[document.status] || {
    label: document.status,
    badge: "bg-slate-100 text-slate-700 border-slate-200",
    desc: "Current status: " + document.status
  };

  // Highlight search text helper
  const renderHighlightedText = (text: string) => {
    if (!searchQuery.trim()) return text;
    const parts = text.split(new RegExp(`(${searchQuery.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&')})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === searchQuery.toLowerCase() ? (
        <mark key={i} className="bg-amber-200 text-amber-900 rounded px-1 font-semibold">{part}</mark>
      ) : (
        part
      )
    );
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      {/* Top Back Navigation */}
      <div className="flex items-center justify-between">
        <Link 
          to="/documents" 
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors group"
        >
          <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" />
          <span>Back to All Documents</span>
        </Link>

        {/* Quick jump to AI Search */}
        <Link
          to={`/search?q=${encodeURIComponent(document.title)}`}
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Ask AI about this Document →</span>
        </Link>
      </div>

      {/* Action Notifications */}
      {actionSuccess && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between animate-fade-in shadow-xs">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{actionSuccess}</span>
          </div>
          <button onClick={() => setActionSuccess(null)} className="text-xs font-bold text-emerald-600 hover:text-emerald-800">✕</button>
        </div>
      )}
      {actionError && (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between animate-fade-in shadow-xs">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{actionError}</span>
          </div>
          <button onClick={() => setActionError(null)} className="text-xs font-bold text-rose-600 hover:text-rose-800">✕</button>
        </div>
      )}

      {/* DOCUMENT HERO HEADER CARD */}
      <div className="bg-white p-6 sm:p-7 rounded-2xl border border-slate-200/90 shadow-card flex flex-col lg:flex-row justify-between items-start lg:items-center gap-5">
        <div className="space-y-2 max-w-2xl">
          <div className="flex items-center space-x-2.5 flex-wrap gap-y-1">
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
              {document.title}
            </h1>
            <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${currentStatusInfo.badge}`}>
              {currentStatusInfo.label}
            </span>
          </div>

          {/* Document metadata pills */}
          <div className="flex items-center gap-3 text-xs text-slate-500 flex-wrap">
            <span className="inline-flex items-center space-x-1 text-slate-600 font-medium">
              <Building className="w-3.5 h-3.5 text-slate-400" />
              <span className="capitalize">{document.department || "General"}</span>
            </span>
            <span>•</span>
            <span className="inline-flex items-center space-x-1 text-slate-600 font-medium">
              <Lock className="w-3.5 h-3.5 text-slate-400" />
              <span className="capitalize">{document.classification || "Internal"}</span>
            </span>
            <span>•</span>
            <span className="inline-flex items-center space-x-1 font-mono text-[11px] text-slate-400">
              <span>ID: {document.id}</span>
            </span>
            <span>•</span>
            <span className="inline-flex items-center space-x-1 text-slate-500">
              <User className="w-3.5 h-3.5 text-slate-400" />
              <span>{document.creator_email || "Creator"}</span>
            </span>
          </div>
        </div>

        {/* PRIMARY WORKFLOW ACTION BUTTONS */}
        <div className="flex flex-wrap items-center gap-2 self-stretch sm:self-auto justify-start sm:justify-end border-t lg:border-t-0 pt-3 lg:pt-0 border-slate-100">
          {/* Action: Submit for Review (DRAFT) */}
          {document.status === "DRAFT" && user?.role !== "VIEWER" && (
            <button
              onClick={() => handleTransition("submit")}
              className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm hover:shadow transition-all"
            >
              <Send className="w-3.5 h-3.5 mr-1.5" />
              Submit for Approval
            </button>
          )}

          {/* Action: Approve / Reject (UNDER_REVIEW) */}
          {document.status === "UNDER_REVIEW" && isApprover && (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleTransition("approve")}
                className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition-all"
              >
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                Approve Document
              </button>
              <button
                onClick={() => handleTransition("reject")}
                className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-bold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 transition-colors"
              >
                <XCircle className="w-3.5 h-3.5 mr-1.5" />
                Reject
              </button>
            </div>
          )}

          {/* Action: Archive (APPROVED) */}
          {document.status === "APPROVED" && isApprover && (
            <button
              onClick={() => handleTransition("archive")}
              className="inline-flex items-center px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-900 text-white shadow-xs transition-colors"
            >
              <Archive className="w-3.5 h-3.5 mr-1.5" />
              Archive
            </button>
          )}

          {/* Share Button */}
          {(isDeleter || user?.id === document.created_by) && (
            <button
              onClick={() => setIsShareOpen(true)}
              className="inline-flex items-center px-3 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
            >
              <Share2 className="w-3.5 h-3.5 mr-1.5 text-slate-500" />
              Share Access
            </button>
          )}

          {/* Delete Button */}
          {isDeleter && (
            <button
              onClick={handleDelete}
              title="Delete Document"
              className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* STATUS EXPLANATION BANNER */}
      <div className="p-4 rounded-xl bg-slate-100/80 border border-slate-200/80 flex items-start sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-indigo-600 shrink-0" />
          <span className="text-xs text-slate-700">
            <strong>Lifecycle Stage:</strong> {currentStatusInfo.desc}
          </span>
        </div>
        <span className="text-[11px] font-mono text-slate-400 shrink-0 hidden sm:inline">
          {new Date(document.updated_at).toLocaleDateString()}
        </span>
      </div>

      {/* MODERN TAB NAVIGATION */}
      <div className="flex items-center border-b border-slate-200/80 pb-1 gap-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab("reader")}
          className={`inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
            activeTab === "reader"
              ? "bg-indigo-600 text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>Read Document</span>
        </button>

        <button
          onClick={() => setActiveTab("workflow")}
          className={`inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
            activeTab === "workflow"
              ? "bg-indigo-600 text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>Approval Timeline</span>
          {history.length > 0 && (
            <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold ${
              activeTab === "workflow" ? "bg-white/20 text-white" : "bg-slate-200 text-slate-700"
            }`}>
              {history.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("properties")}
          className={`inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
            activeTab === "properties"
              ? "bg-indigo-600 text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <Database className="w-4 h-4" />
          <span>Properties & Metadata</span>
        </button>

        <button
          onClick={() => setActiveTab("audit")}
          className={`inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
            activeTab === "audit"
              ? "bg-indigo-600 text-white shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Security & Audit Chain</span>
          {auditLogs.length > 0 && (
            <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold ${
              activeTab === "audit" ? "bg-white/20 text-white" : "bg-slate-200 text-slate-700"
            }`}>
              {auditLogs.length}
            </span>
          )}
        </button>
      </div>

      {/* ======================================================== */}
      {/* TAB 1: DOCUMENT READER (THE MAIN FOCUS)                   */}
      {/* ======================================================== */}
      {activeTab === "reader" && (
        <div className="space-y-6">
          {/* AI SUMMARY BOX */}
          {docContent?.summary && (
            <div className="p-5 rounded-2xl bg-gradient-to-r from-indigo-50/90 via-violet-50/70 to-indigo-50/50 border border-indigo-200/80 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-indigo-900 font-bold text-xs uppercase tracking-wider">
                  <Sparkles className="w-4 h-4 text-indigo-600" />
                  <span>AI Executive Summary & Key Highlights</span>
                </div>
                <span className="text-[10px] uppercase font-bold text-indigo-600 bg-white/80 px-2 py-0.5 rounded-full border border-indigo-200">
                  Auto-Extracted
                </span>
              </div>
              <p className="text-xs sm:text-sm text-indigo-950/80 leading-relaxed font-normal">
                {docContent.summary}
              </p>
            </div>
          )}

          {/* READER TOOLBAR */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200/90 shadow-card flex flex-col sm:flex-row items-center justify-between gap-3">
            {/* Search within document */}
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search words in document text..."
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
              />
              {searchQuery && (
                <button 
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2.5 top-2 text-slate-400 hover:text-slate-600 text-xs"
                >
                  ✕
                </button>
              )}
            </div>

            {/* View Mode & Stats */}
            <div className="flex items-center space-x-3 w-full sm:w-auto justify-between sm:justify-end text-xs text-slate-500">
              <div className="flex items-center space-x-1.5 font-medium">
                <span>{docContent?.total_words || 0} words</span>
                <span>•</span>
                <span>{docContent?.total_pages || 1} page{docContent?.total_pages !== 1 ? 's' : ''}</span>
              </div>

              {/* Copy Full Text */}
              <button
                onClick={handleCopyFullText}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 font-semibold transition-colors"
              >
                {copiedText ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="text-emerald-700">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-slate-500" />
                    <span>Copy Text</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* DOCUMENT PAGES CANVAS */}
          {contentLoading ? (
            <div className="bg-white p-16 rounded-2xl border border-slate-200 text-center">
              <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-xs text-slate-400">Loading document text...</p>
            </div>
          ) : docContent && docContent.pages && docContent.pages.length > 0 ? (
            <div className="space-y-6">
              {docContent.pages.map((p) => (
                <div 
                  key={p.page}
                  className="bg-white p-8 sm:p-12 rounded-2xl border border-slate-200/90 shadow-card space-y-4 max-w-4xl mx-auto relative group hover:border-slate-300 transition-colors"
                >
                  {/* Page Header Ribbon */}
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3 text-xs text-slate-400 font-mono">
                    <span className="font-bold text-slate-600">
                      PAGE {p.page} OF {docContent.total_pages}
                    </span>
                    <span>{p.word_count} WORDS</span>
                  </div>

                  {/* Rendered Document Body */}
                  <div className="text-slate-800 text-sm sm:text-base leading-relaxed whitespace-pre-line font-serif selection:bg-indigo-100">
                    {renderHighlightedText(p.text)}
                  </div>

                  {/* Page Footer */}
                  <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                    <span>DocIntel Encrypted Ingestion</span>
                    <span className="font-mono">Page {p.page}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-3">
              <FileText className="w-8 h-8 text-slate-300 mx-auto" />
              <h3 className="text-sm font-bold text-slate-700">No Extracted Text Found</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                This document is recorded in the platform catalog but has not had text extracted yet.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 2: APPROVAL WORKFLOW & TIMELINE                      */}
      {/* ======================================================== */}
      {activeTab === "workflow" && (
        <div className="space-y-6">
          {/* Stepper Card */}
          <div className="bg-white p-6 sm:p-7 rounded-2xl border border-slate-200/90 shadow-card space-y-6">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Document Lifecycle Stage
            </h3>

            {/* Stepper */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              {[
                { label: "Draft", desc: "Uploaded by team contributor", active: true },
                { 
                  label: "Under Review", 
                  desc: "Manager inspection & dual custody", 
                  active: document.status !== "DRAFT" 
                },
                { 
                  label: document.status === "REJECTED" ? "Rejected" : "Approved", 
                  desc: document.status === "REJECTED" ? "Requires revision" : "Active in corporate search", 
                  active: document.status === "APPROVED" || document.status === "REJECTED" || document.status === "ARCHIVED" 
                },
                { 
                  label: "Archived", 
                  desc: "Permanent historical storage", 
                  active: document.status === "ARCHIVED" 
                }
              ].map((st, idx) => (
                <div 
                  key={st.label} 
                  className={`p-4 rounded-xl border transition-all ${
                    st.active 
                      ? "bg-indigo-50/50 border-indigo-200 text-indigo-950" 
                      : "bg-slate-50/60 border-slate-200 text-slate-400 opacity-60"
                  }`}
                >
                  <div className="flex items-center space-x-2 mb-1.5">
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                      st.active ? "bg-indigo-600 text-white" : "bg-slate-300 text-slate-600"
                    }`}>
                      {idx + 1}
                    </span>
                    <span className="font-bold text-xs">{st.label}</span>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-snug">{st.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Chronological Transition History */}
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-card overflow-hidden">
            <div className="p-4 border-b border-slate-100 font-bold text-xs uppercase tracking-wider text-slate-700">
              Audit-Verified Transition History
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-100 text-left text-xs">
                <thead className="bg-slate-50/75 text-slate-500 uppercase font-semibold">
                  <tr>
                    <th className="px-5 py-3">State Transition</th>
                    <th className="px-5 py-3">Authorized By</th>
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
                      <td className="px-5 py-3 text-slate-600 font-medium">{h.actor_email || `User #${h.actor_id}`}</td>
                      <td className="px-5 py-3 text-slate-400 font-mono text-[11px]">{new Date(h.timestamp).toLocaleString()}</td>
                    </tr>
                  ))}
                  {history.length === 0 && (
                    <tr>
                      <td colSpan={3} className="px-5 py-6 text-center text-slate-400">
                        No transitions recorded yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 3: PROPERTIES & METADATA                             */}
      {/* ======================================================== */}
      {activeTab === "properties" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-card space-y-4">
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-900 border-b border-slate-100 pb-2.5 flex items-center">
              <Database className="w-3.5 h-3.5 mr-2 text-indigo-600" />
              Document Properties
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Document ID:</span>
                <span className="font-mono font-bold text-slate-800">{document.id}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Department:</span>
                <span className="font-semibold capitalize text-slate-800">{document.department}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Security Classification:</span>
                <span className="font-semibold capitalize text-slate-800">{document.classification}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Status:</span>
                <span className="font-bold text-slate-800">{document.status}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Vendor / Counterparty:</span>
                <span className="text-slate-700">{document.metadata?.vendor || "None specified"}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Tenant Workspace:</span>
                <span className="font-mono text-slate-600">{document.tenant_id}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Created:</span>
                <span className="font-mono text-[11px]">{new Date(document.created_at).toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Last Modified:</span>
                <span className="font-mono text-[11px]">{new Date(document.updated_at).toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-card space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <h3 className="font-bold text-xs uppercase tracking-wider text-slate-900 flex items-center">
                <Tag className="w-3.5 h-3.5 mr-2 text-emerald-600" />
                Tags & Extended Attributes
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

            {/* Tags list */}
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Document Tags
              </span>
              <div className="flex flex-wrap gap-1.5">
                {document.metadata?.tags && document.metadata.tags.length > 0 ? (
                  document.metadata.tags.map((t: string, idx: number) => (
                    <span key={idx} className="px-2.5 py-1 rounded-lg text-xs bg-indigo-50 text-indigo-700 font-semibold border border-indigo-200">
                      #{t}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-400">No tags assigned</span>
                )}
              </div>
            </div>

            {/* Raw JSON viewer */}
            <div className="pt-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
                Flexible Metadata Store
              </span>
              <pre className="bg-slate-900 text-slate-100 p-4 rounded-xl text-xs font-mono overflow-x-auto max-h-56 shadow-inner">
                {JSON.stringify(document.metadata, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* TAB 4: CRYPTOGRAPHIC AUDIT CHAIN                         */}
      {/* ======================================================== */}
      {activeTab === "audit" && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200/90 shadow-card flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600">
                <ShieldCheck className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Tamper-Evident SHA-256 Ledger
                </h3>
                <p className="text-xs text-slate-500">
                  Every change to this document forms a forward-chained cryptographic block.
                </p>
              </div>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Chain Verified ✓
            </span>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-card overflow-hidden">
            <div className="p-4 border-b border-slate-100 font-bold text-xs uppercase tracking-wider text-slate-700">
              Audit Event Log ({auditLogs.length} Records)
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-100 text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
                  <tr>
                    <th className="px-5 py-3">Event Action</th>
                    <th className="px-5 py-3">Actor</th>
                    <th className="px-5 py-3">Current Hash</th>
                    <th className="px-5 py-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {auditLogs.map((log) => (
                    <tr key={log.id}>
                      <td className="px-5 py-3 font-semibold text-slate-900">
                        {log.action}
                      </td>
                      <td className="px-5 py-3 text-slate-600">
                        {log.actor_email || `User #${log.actor_id || "SYSTEM"}`}
                      </td>
                      <td className="px-5 py-3 font-mono text-[11px] text-slate-500">
                        <button
                          onClick={() => handleCopyHash(log.current_hash)}
                          className="hover:text-indigo-600 flex items-center space-x-1"
                          title="Click to copy SHA-256 hash"
                        >
                          <span>{log.current_hash.slice(0, 16)}...</span>
                          <Copy className="w-3 h-3 text-slate-400" />
                        </button>
                      </td>
                      <td className="px-5 py-3 font-mono text-[11px] text-slate-400">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                  {auditLogs.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-5 py-6 text-center text-slate-400">
                        No audit events recorded for this document yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* SHARE MODAL */}
      {isShareOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-modal border border-slate-200 animate-fade-in space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-sm text-slate-900 flex items-center space-x-2">
                <Share2 className="w-4 h-4 text-indigo-600" />
                <span>Grant Document Access Policy</span>
              </h3>
              <button 
                onClick={() => setIsShareOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleShareSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Grantee Type</label>
                <select 
                  value={granteeType}
                  onChange={(e: any) => setGranteeType(e.target.value)}
                  className="w-full p-2 border border-slate-200 rounded-xl bg-slate-50"
                >
                  <option value="USER">Specific User ID</option>
                  <option value="ROLE">Specific Role (e.g. EMPLOYEE)</option>
                  <option value="DEPARTMENT">Specific Department (e.g. engineering)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Grantee Identifier</label>
                <input 
                  type="text"
                  required
                  value={granteeId}
                  onChange={(e) => setGranteeId(e.target.value)}
                  placeholder={granteeType === "USER" ? "e.g. 2" : granteeType === "ROLE" ? "e.g. EMPLOYEE" : "e.g. finance"}
                  className="w-full p-2 border border-slate-200 rounded-xl"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Permission Level</label>
                <select 
                  value={permissionLevel}
                  onChange={(e) => setPermissionLevel(e.target.value)}
                  className="w-full p-2 border border-slate-200 rounded-xl bg-slate-50"
                >
                  <option value="READ">READ (View document content)</option>
                  <option value="WRITE">WRITE (Edit draft metadata)</option>
                  <option value="ADMIN">ADMIN (Full administrative rights)</option>
                </select>
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsShareOpen(false)}
                  className="px-3 py-1.5 rounded-xl border border-slate-200 text-slate-600 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={sharing}
                  className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold shadow-xs"
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
