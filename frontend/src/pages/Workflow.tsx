import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { 
  GitPullRequest, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  Archive, 
  FileText, 
  Send, 
  ArrowRight,
  Layers,
  Inbox
} from "lucide-react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export const Workflow: React.FC = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const res = await api.get("/documents");
      setDocuments(res.data || []);
    } catch (err) {
      console.error("Workflow fetch failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleAction = async (docId: string, action: string) => {
    setActionNotice(null);
    try {
      const res = await api.post(`/documents/${docId}/${action}`);
      setActionNotice(res.data.message);
      await loadDocuments();
    } catch (err: any) {
      setActionNotice(err.response?.data?.detail || "Action failed.");
    }
  };

  const columns = [
    { key: "DRAFT", title: "Draft", icon: FileText, badgeColor: "text-blue-700 bg-blue-50 border-blue-200/80", accent: "border-blue-500" },
    { key: "UNDER_REVIEW", title: "Under Review", icon: Clock, badgeColor: "text-amber-700 bg-amber-50 border-amber-200/80", accent: "border-amber-500" },
    { key: "APPROVED", title: "Approved", icon: CheckCircle2, badgeColor: "text-emerald-700 bg-emerald-50 border-emerald-200/80", accent: "border-emerald-500" },
    { key: "REJECTED", title: "Rejected", icon: XCircle, badgeColor: "text-rose-700 bg-rose-50 border-rose-200/80", accent: "border-rose-500" },
    { key: "ARCHIVED", title: "Archived", icon: Archive, badgeColor: "text-slate-700 bg-slate-100 border-slate-200", accent: "border-slate-400" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">
          Document Approval Workflows
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Track, review, and approve enterprise documents through authorized lifecycle stages
        </p>
      </div>

      {actionNotice && (
        <div className="p-3.5 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-900 text-xs flex items-center justify-between animate-fade-in">
          <span>{actionNotice}</span>
          <button onClick={() => setActionNotice(null)} className="text-xs font-bold text-indigo-600 hover:text-indigo-800">✕</button>
        </div>
      )}

      {/* Kanban Columns */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3.5 items-start">
        {columns.map((col) => {
          const Icon = col.icon;
          const colDocs = documents.filter((d) => d.status === col.key);

          return (
            <div key={col.key} className="flex flex-col bg-slate-100/60 rounded-2xl border border-slate-200/80 overflow-hidden min-h-[540px]">
              {/* Column Header */}
              <div className={`p-3 bg-white border-t-2 ${col.accent} border-b border-slate-200/80 flex items-center justify-between`}>
                <div className="flex items-center space-x-1.5">
                  <Icon className="w-3.5 h-3.5 text-slate-600" />
                  <span className="font-bold text-[11px] uppercase tracking-wider text-slate-800">{col.title}</span>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.2 rounded-full border ${col.badgeColor}`}>
                  {colDocs.length}
                </span>
              </div>

              {/* Column Cards */}
              <div className="p-2.5 flex-1 space-y-2.5 overflow-y-auto max-h-[640px]">
                {colDocs.map((doc) => (
                  <div key={doc.id} className="p-3 rounded-xl border border-slate-200/80 bg-white hover:border-indigo-300 shadow-card hover:shadow-card-hover transition-all space-y-2 group">
                    <Link to={`/documents/${doc.id}`} className="font-semibold text-xs text-slate-900 group-hover:text-indigo-600 block line-clamp-2 transition-colors">
                      {doc.title}
                    </Link>
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <span className="font-mono text-indigo-600 font-semibold">{doc.id}</span>
                      <span className="capitalize px-1.5 py-0.2 rounded-md bg-slate-100 text-slate-600 font-medium border border-slate-200/60">{doc.department}</span>
                    </div>

                    {/* Available Actions per Role */}
                    <div className="pt-2 border-t border-slate-100 flex items-center justify-end gap-1">
                      {doc.status === "DRAFT" && user?.role !== "VIEWER" && (
                        <button
                          onClick={() => handleAction(doc.id, "submit")}
                          className="text-[10px] font-semibold px-2 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-2xs transition-colors"
                        >
                          Submit →
                        </button>
                      )}

                      {doc.status === "UNDER_REVIEW" && (user?.role === "SUPER_ADMIN" || user?.role === "ADMIN" || user?.role === "MANAGER") && (
                        <>
                          <button
                            onClick={() => handleAction(doc.id, "approve")}
                            className="text-[10px] font-semibold px-2 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white shadow-2xs transition-colors"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleAction(doc.id, "reject")}
                            className="text-[10px] font-semibold px-2 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200/80 transition-colors"
                          >
                            Reject
                          </button>
                        </>
                      )}

                      {doc.status === "APPROVED" && (user?.role === "SUPER_ADMIN" || user?.role === "ADMIN" || user?.role === "MANAGER") && (
                        <button
                          onClick={() => handleAction(doc.id, "archive")}
                          className="text-[10px] font-semibold px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-900 text-white shadow-2xs transition-colors"
                        >
                          Archive
                        </button>
                      )}

                      <Link
                        to={`/documents/${doc.id}`}
                        className="text-[10px] text-slate-400 hover:text-indigo-600 px-1 py-1 transition-colors"
                      >
                        Inspect
                      </Link>
                    </div>
                  </div>
                ))}

                {colDocs.length === 0 && (
                  <div className="text-center py-14 text-slate-400">
                    <Inbox className="w-6 h-6 mx-auto mb-1.5 opacity-30 text-slate-400" />
                    <p className="text-[11px] font-medium text-slate-400">No documents</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

