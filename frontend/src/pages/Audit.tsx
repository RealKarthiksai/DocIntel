import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { 
  ShieldCheck, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  Key, 
  Lock, 
  Activity, 
  FileText,
  Copy,
  Check
} from "lucide-react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export const Audit: React.FC = () => {
  const { user } = useAuth();
  const [logs, setLogs] = useState<any[]>([]);
  const [verification, setVerification] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const res = await api.get("/audit?limit=100");
      setLogs(res.data || []);
    } catch (err) {
      console.error("Audit log fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const verifyChain = async () => {
    try {
      setVerifying(true);
      const res = await api.get("/audit/verify");
      setVerification(res.data);
    } catch (err: any) {
      if (err.response?.status === 403) {
        setVerification({
          is_valid: null,
          is_forbidden: true,
          details: "Access Restricted: Cryptographic audit verification requires MANAGER, ADMIN, or SUPER_ADMIN authorization."
        });
      } else {
        setVerification({
          is_valid: false,
          is_forbidden: false,
          details: err.response?.data?.detail || "Verification failed."
        });
      }
    } finally {
      setVerifying(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    verifyChain();
  }, []);

  const handleCopyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header & Verification Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center">
            <ShieldCheck className="w-6 h-6 text-indigo-600 mr-2" />
            Cryptographic Audit Ledger
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Tamper-evident SHA-256 block hash chaining guaranteeing forensic immutability
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="p-2 border border-slate-300/80 rounded-xl hover:bg-slate-50 text-slate-600 transition-colors bg-white shadow-2xs"
            title="Refresh Logs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={verifyChain}
            disabled={verifying}
            className="inline-flex items-center px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl shadow-xs transition-all hover:shadow-sm disabled:opacity-50"
          >
            <Lock className="w-3.5 h-3.5 mr-1.5" />
            {verifying ? "Verifying SHA-256 Hashes..." : "Verify Chain Integrity"}
          </button>
        </div>
      </div>

      {/* Verification Status Banner */}
      {verification && (
        <div className={`p-4 sm:p-5 rounded-2xl border ${
          verification.is_forbidden
            ? "bg-amber-50/70 border-amber-200/80 text-amber-900"
            : verification.is_valid 
            ? "bg-emerald-50/70 border-emerald-200/80 text-emerald-900" 
            : "bg-rose-50/70 border-rose-200/80 text-rose-900"
        } shadow-card flex items-start justify-between animate-fade-in`}>
          <div className="flex items-start space-x-3">
            {verification.is_forbidden ? (
              <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
            ) : verification.is_valid ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5 shrink-0" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-rose-600 mt-0.5 shrink-0" />
            )}
            <div>
              <div className="font-bold text-xs uppercase tracking-wider">
                {verification.is_forbidden
                  ? "Audit Access Restricted"
                  : verification.is_valid 
                  ? "Cryptographic Chain Integrity Verified" 
                  : "Chain Integrity Tamper Detected"}
              </div>
              <div className="text-xs mt-1 text-slate-600 leading-relaxed">{verification.details}</div>
              {verification.total_records !== undefined && (
                <div className="text-[11px] text-slate-400 mt-1 font-mono">
                  Verified Blocks: <strong className="text-slate-700">{verification.total_records}</strong> | Checked: {new Date().toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>
          <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold border uppercase shrink-0 ${
            verification.is_forbidden
              ? "bg-amber-100 text-amber-800 border-amber-200"
              : verification.is_valid 
              ? "bg-emerald-100 text-emerald-800 border-emerald-200" 
              : "bg-rose-100 text-rose-800 border-rose-200"
          }`}>
            {verification.is_forbidden ? "PERMISSION REQUIRED" : verification.is_valid ? "100% UNTAMPERED" : "TAMPERED"}
          </span>
        </div>
      )}

      {/* Audit Log Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-100 text-left text-xs">
            <thead className="bg-slate-50/75 text-slate-500 uppercase font-semibold">
              <tr>
                <th className="px-5 py-3.5">Block ID</th>
                <th className="px-5 py-3.5">Action</th>
                <th className="px-5 py-3.5">Actor</th>
                <th className="px-5 py-3.5">Target Document</th>
                <th className="px-5 py-3.5">Timestamp (UTC)</th>
                <th className="px-5 py-3.5">Payload Preview</th>
                <th className="px-5 py-3.5">SHA-256 Block Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 font-mono">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="px-5 py-3.5 font-bold text-slate-900">#{log.id}</td>
                  <td className="px-5 py-3.5 font-sans font-semibold">
                    <span className="px-2 py-0.5 rounded-full text-[10px] bg-indigo-50 text-indigo-700 border border-indigo-200/80">
                      {log.action}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 font-sans text-slate-600 truncate max-w-[140px]">{log.actor_email || `User #${log.actor_id}`}</td>
                  <td className="px-5 py-3.5 text-indigo-600 font-bold">
                    {log.document_id ? (
                      <Link to={`/documents/${log.document_id}`} className="hover:underline hover:text-indigo-800">
                        {log.document_id}
                      </Link>
                    ) : (
                      <span className="text-slate-300 font-sans">—</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5 font-sans text-slate-400 text-[11px]">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-5 py-3.5 text-[10px] text-slate-500 max-w-xs truncate font-mono">
                    {JSON.stringify(log.metadata)}
                  </td>
                  <td className="px-5 py-3.5 text-[10px] text-slate-500 whitespace-nowrap">
                    <button
                      onClick={() => handleCopyHash(log.current_hash)}
                      className="group flex items-center space-x-1.5 hover:text-indigo-600 transition-colors"
                      title="Click to copy full SHA-256 hash"
                    >
                      <span className="font-bold text-slate-800 group-hover:text-indigo-700">
                        {log.current_hash.slice(0, 12)}...
                      </span>
                      {copiedHash === log.current_hash ? (
                        <Check className="w-3 h-3 text-emerald-600" />
                      ) : (
                        <Copy className="w-3 h-3 text-slate-300 group-hover:text-indigo-500" />
                      )}
                    </button>
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-slate-400 font-sans">
                    No audit records found in the ledger.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

