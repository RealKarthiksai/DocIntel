import React, { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { 
  FileText, 
  Upload, 
  Search, 
  Filter, 
  Plus, 
  X, 
  CheckCircle2, 
  AlertCircle,
  Tag,
  Building,
  Shield,
  Layers,
  ArrowRight
} from "lucide-react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export const Documents: React.FC = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [searchParams] = useSearchParams();
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  useEffect(() => {
    if (searchParams.get("upload") === "true" && user?.role !== "VIEWER") {
      setIsUploadOpen(true);
    }
  }, [searchParams, user]);

  // Upload Form State
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [department, setDepartment] = useState("general");
  const [classification, setClassification] = useState("internal");
  const [vendor, setVendor] = useState("");
  const [tagsInput, setTagsInput] = useState("");
  const [customFields, setCustomFields] = useState<{ key: string; value: string }[]>([
    { key: "risk_level", value: "medium" },
  ]);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const res = await api.get("/documents");
      setDocuments(res.data || []);
    } catch (err) {
      console.error("Error fetching documents:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleAddCustomField = () => {
    setCustomFields([...customFields, { key: "", value: "" }]);
  };

  const handleCustomFieldChange = (index: number, key: string, value: string) => {
    const updated = [...customFields];
    updated[index] = { key, value };
    setCustomFields(updated);
  };

  const handleRemoveCustomField = (index: number) => {
    setCustomFields(customFields.filter((_, i) => i !== index));
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setUploadError("Please select a valid PDF or DOCX file.");
      return;
    }

    setUploadError(null);
    setUploadSuccess(null);
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title || file.name);
    formData.append("department", department);
    formData.append("classification", classification);
    formData.append("vendor", vendor);

    const parsedTags = tagsInput.split(",").map((t) => t.trim()).filter(Boolean);
    formData.append("tags", JSON.stringify(parsedTags));

    const customFieldsObj: Record<string, any> = {};
    customFields.forEach((cf) => {
      if (cf.key.trim()) {
        customFieldsObj[cf.key.trim()] = cf.value.trim();
      }
    });
    formData.append("custom_fields", JSON.stringify(customFieldsObj));

    try {
      const res = await api.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadSuccess(`Document '${res.data.title}' successfully ingested as ${res.data.id}!`);
      setIsUploadOpen(false);
      // Reset form
      setFile(null);
      setTitle("");
      setVendor("");
      setTagsInput("");
      fetchDocuments();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || "Upload failed. Please check file format and permissions.");
    } finally {
      setUploading(false);
    }
  };

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) || doc.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDept = departmentFilter === "ALL" || (doc.department && doc.department.toLowerCase() === departmentFilter.toLowerCase());
    const matchesStatus = statusFilter === "ALL" || doc.status === statusFilter;
    return matchesSearch && matchesDept && matchesStatus;
  });

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

  const classificationBadge = (classification: string) => {
    switch (classification) {
      case "confidential":
        return <span className="px-2 py-0.2 rounded-md text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200/80 uppercase">Confidential</span>;
      case "restricted":
        return <span className="px-2 py-0.2 rounded-md text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200/80 uppercase">Restricted</span>;
      case "public":
        return <span className="px-2 py-0.2 rounded-md text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200/80 uppercase">Public</span>;
      default:
        return <span className="px-2 py-0.2 rounded-md text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200/80 uppercase">Internal</span>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header & Upload Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Document Repository
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Polyglot storage with departmental boundaries and vector indexing
          </p>
        </div>
        {user?.role !== "VIEWER" && (
          <button
            onClick={() => setIsUploadOpen(true)}
            className="inline-flex items-center px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl shadow-xs transition-all hover:shadow-sm"
          >
            <Upload className="w-3.5 h-3.5 mr-1.5" />
            Upload New Document
          </button>
        )}
      </div>

      {uploadSuccess && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between animate-fade-in">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{uploadSuccess}</span>
          </div>
          <button onClick={() => setUploadSuccess(null)} className="text-emerald-600 hover:text-emerald-800">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Filter & Search Toolbar */}
      <div className="bg-white p-3.5 rounded-2xl border border-slate-200/80 shadow-card flex flex-col sm:flex-row gap-3 justify-between items-center">
        <div className="relative w-full sm:w-80">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Filter by title or DOC-ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3.5 py-2 bg-slate-50/50 border border-slate-300/80 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all placeholder-slate-400"
          />
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          <select
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
            className="px-3 py-2 border border-slate-300/80 rounded-xl text-xs bg-slate-50/50 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
          >
            <option value="ALL">All Departments</option>
            <option value="general">General</option>
            <option value="finance">Finance</option>
            <option value="engineering">Engineering</option>
            <option value="hr">Human Resources</option>
            <option value="legal">Legal</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-slate-300/80 rounded-xl text-xs bg-slate-50/50 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
          >
            <option value="ALL">All Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </div>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-100 text-left text-xs">
            <thead className="bg-slate-50/75 text-slate-500 uppercase font-semibold">
              <tr>
                <th className="px-6 py-3.5">Document</th>
                <th className="px-6 py-3.5">Department</th>
                <th className="px-6 py-3.5">Classification</th>
                <th className="px-6 py-3.5">Status</th>
                <th className="px-6 py-3.5">Created At</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {filteredDocs.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="px-6 py-4">
                    <Link to={`/documents/${doc.id}`} className="font-semibold text-indigo-600 hover:text-indigo-800 block truncate max-w-[280px]">
                      {doc.title}
                    </Link>
                    <div className="text-[10px] text-slate-400 font-mono mt-0.5">{doc.id}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="capitalize px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-700 border border-slate-200/80">
                      {doc.department || "general"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {classificationBadge(doc.classification)}
                  </td>
                  <td className="px-6 py-4">
                    {statusBadge(doc.status)}
                  </td>
                  <td className="px-6 py-4 text-slate-500 font-mono text-[11px]">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      to={`/documents/${doc.id}`}
                      className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200/80 transition-colors"
                    >
                      Details & Workflow
                    </Link>
                  </td>
                </tr>
              ))}
              {filteredDocs.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                    No documents matching the current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Upload Document Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-modal border border-slate-200 space-y-5 animate-fade-in">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3.5">
              <div>
                <h3 className="text-base font-bold text-slate-900">Upload Enterprise Document</h3>
                <p className="text-[11px] text-slate-400 mt-0.5">PDF or DOCX binary with multi-model indexing</p>
              </div>
              <button onClick={() => setIsUploadOpen(false)} className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100">
                <X className="w-4 h-4" />
              </button>
            </div>

            {uploadError && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
                {uploadError}
              </div>
            )}

            <form onSubmit={handleUploadSubmit} className="space-y-4 text-xs">
              {/* File Dropzone */}
              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Binary Document File *
                </label>
                <div className="p-4 rounded-xl border-2 border-dashed border-slate-200 hover:border-indigo-400 transition-colors bg-slate-50/50 text-center">
                  <input
                    type="file"
                    required
                    id="doc-file-input"
                    accept=".pdf,.docx"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setFile(e.target.files[0]);
                        if (!title) setTitle(e.target.files[0].name.replace(/\.[^/.]+$/, ""));
                      }
                    }}
                    className="hidden"
                  />
                  <label htmlFor="doc-file-input" className="cursor-pointer block">
                    <FileText className="w-8 h-8 mx-auto text-indigo-500 mb-1.5" />
                    <div className="text-xs font-semibold text-slate-800">
                      {file ? file.name : "Click to select or drag PDF / DOCX"}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      {file ? `${(file.size / 1024).toFixed(1)} KB selected` : "Automatic OCR & 384-d vector embeddings"}
                    </div>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Document Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Master Services Agreement"
                  className="w-full px-3 py-2 bg-slate-50/50 border border-slate-300/80 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white focus:outline-none transition-all"
                />
              </div>

              <div className="grid grid-cols-2 gap-3.5">
                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Department *
                  </label>
                  <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50/50 border border-slate-300/80 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white focus:outline-none transition-all"
                  >
                    <option value="general">General</option>
                    <option value="finance">Finance</option>
                    <option value="engineering">Engineering</option>
                    <option value="hr">Human Resources</option>
                    <option value="legal">Legal</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                    Classification
                  </label>
                  <select
                    value={classification}
                    onChange={(e) => setClassification(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50/50 border border-slate-300/80 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white focus:outline-none transition-all"
                  >
                    <option value="internal">Internal</option>
                    <option value="confidential">Confidential</option>
                    <option value="public">Public</option>
                    <option value="restricted">Restricted</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Vendor / Counterparty
                </label>
                <input
                  type="text"
                  value={vendor}
                  onChange={(e) => setVendor(e.target.value)}
                  placeholder="e.g. Acme Technologies Corp"
                  className="w-full px-3 py-2 bg-slate-50/50 border border-slate-300/80 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white focus:outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Tags (comma separated)
                </label>
                <input
                  type="text"
                  value={tagsInput}
                  onChange={(e) => setTagsInput(e.target.value)}
                  placeholder="contract, invoice, cloud"
                  className="w-full px-3 py-2 bg-slate-50/50 border border-slate-300/80 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:bg-white focus:outline-none transition-all"
                />
              </div>

              {/* Dynamic MongoDB Custom Fields */}
              <div className="pt-2 border-t border-slate-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600">
                    MongoDB Schema-Free Metadata
                  </span>
                  <button
                    type="button"
                    onClick={handleAddCustomField}
                    className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center"
                  >
                    <Plus className="w-3 h-3 mr-1" /> Add Field
                  </button>
                </div>

                <div className="space-y-2 max-h-32 overflow-y-auto pr-1">
                  {customFields.map((cf, idx) => (
                    <div key={idx} className="flex gap-2 items-center">
                      <input
                        type="text"
                        placeholder="Key (e.g. renewal_period)"
                        value={cf.key}
                        onChange={(e) => handleCustomFieldChange(idx, e.target.value, cf.value)}
                        className="w-1/2 px-2.5 py-1.5 bg-slate-50/50 border border-slate-300/80 rounded-lg text-xs"
                      />
                      <input
                        type="text"
                        placeholder="Value (e.g. 12 months)"
                        value={cf.value}
                        onChange={(e) => handleCustomFieldChange(idx, cf.key, e.target.value)}
                        className="w-1/2 px-2.5 py-1.5 bg-slate-50/50 border border-slate-300/80 rounded-lg text-xs"
                      />
                      <button
                        type="button"
                        onClick={() => handleRemoveCustomField(idx)}
                        className="text-slate-400 hover:text-rose-600 p-1"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-3.5 flex justify-end gap-2.5 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsUploadOpen(false)}
                  className="px-3.5 py-2 border border-slate-300/80 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-all disabled:opacity-50"
                >
                  {uploading ? "Ingesting & Embedding..." : "Ingest Document"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

