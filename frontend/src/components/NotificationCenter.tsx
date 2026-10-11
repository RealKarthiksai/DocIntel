import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { 
  Bell, 
  Check, 
  CheckCheck, 
  Clock, 
  FileUp, 
  AlertCircle, 
  CheckCircle2, 
  Archive, 
  Radio
} from "lucide-react";
import api from "../api/client";

interface NotificationItem {
  id: string;
  tenant_id: string;
  recipient_role?: string;
  department: string;
  document_id?: string;
  event_type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export const NotificationCenter: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const fetchNotifications = async () => {
    try {
      const res = await api.get("/notifications?limit=25");
      setNotifications(res.data.notifications || []);
      setUnreadCount(res.data.unread_count || 0);
    } catch (err) {
      // Quiet fail if not logged in
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 5000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  const markAsRead = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.post(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch (err) {
      console.error("Failed to mark notification as read", err);
    }
  };

  const markAllAsRead = async () => {
    try {
      setLoading(true);
      await api.post("/notifications/read-all");
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error("Failed to mark all notifications as read", err);
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (eventType: string, message: string) => {
    if (eventType === "DOCUMENT_UPLOADED") {
      return <FileUp className="w-3.5 h-3.5 text-blue-600" />;
    }
    if (message.includes("approved")) {
      return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />;
    }
    if (message.includes("rejected")) {
      return <AlertCircle className="w-3.5 h-3.5 text-rose-600" />;
    }
    if (message.includes("archived")) {
      return <Archive className="w-3.5 h-3.5 text-amber-600" />;
    }
    return <Clock className="w-3.5 h-3.5 text-indigo-600" />;
  };

  const getDeptColor = (dept: string) => {
    switch (dept.toLowerCase()) {
      case "legal":
        return "bg-purple-50 text-purple-700 border-purple-200/80";
      case "finance":
        return "bg-blue-50 text-blue-700 border-blue-200/80";
      case "engineering":
        return "bg-cyan-50 text-cyan-700 border-cyan-200/80";
      case "hr":
        return "bg-amber-50 text-amber-700 border-amber-200/80";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200/80";
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell Button */}
      <button
        onClick={() => {
          setIsOpen(!isOpen);
          if (!isOpen) fetchNotifications();
        }}
        className="relative p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100/80 transition-colors focus:outline-none"
        title="Kafka Workflow Notifications"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 flex h-3.5 w-3.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-rose-600 text-white text-[9px] font-bold items-center justify-center shadow-xs">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          </span>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 max-w-[92vw] bg-white rounded-2xl shadow-modal border border-slate-200/90 z-50 overflow-hidden animate-fade-in">
          {/* Header */}
          <div className="p-3.5 bg-slate-50/70 border-b border-slate-200/80 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Radio className="w-3.5 h-3.5 text-indigo-600 animate-pulse" />
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Event Notifications
              </h3>
              {unreadCount > 0 && (
                <span className="text-[10px] font-semibold bg-rose-100 text-rose-700 px-1.5 py-0.2 rounded-full border border-rose-200">
                  {unreadCount} new
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                disabled={loading}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center space-x-1 transition-colors"
              >
                <CheckCheck className="w-3.5 h-3.5" />
                <span>Mark all read</span>
              </button>
            )}
          </div>

          {/* List */}
          <div className="max-h-[380px] overflow-y-auto divide-y divide-slate-100">
            {notifications.length === 0 ? (
              <div className="py-10 text-center text-slate-400">
                <Bell className="w-7 h-7 mx-auto mb-2 opacity-30 text-slate-400" />
                <p className="text-xs font-medium text-slate-600">No workflow notifications yet</p>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Real-time events will stream here automatically
                </p>
              </div>
            ) : (
              notifications.map((n) => (
                <div
                  key={n.id}
                  onClick={() => setIsOpen(false)}
                  className={`p-3.5 transition-colors hover:bg-slate-50/80 flex items-start space-x-3 cursor-pointer ${
                    !n.is_read ? "bg-indigo-50/30" : ""
                  }`}
                >
                  <div className="mt-0.5 p-1.5 rounded-lg bg-slate-50 border border-slate-200/80 shrink-0">
                    {getEventIcon(n.event_type, n.message)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="text-xs font-semibold text-slate-900 truncate">
                        {n.title}
                      </span>
                      <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded border uppercase shrink-0 ${getDeptColor(n.department)}`}>
                        {n.department}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 line-clamp-2 leading-relaxed">
                      {n.message}
                    </p>
                    <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-slate-100/80">
                      <span className="text-[10px] text-slate-400 font-mono">
                        {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                      <div className="flex items-center space-x-2">
                        {n.document_id && (
                          <Link
                            to={`/documents/${n.document_id}`}
                            className="text-[10px] text-indigo-600 hover:text-indigo-800 font-semibold transition-colors"
                          >
                            View Doc →
                          </Link>
                        )}
                        {!n.is_read && (
                          <button
                            onClick={(e) => markAsRead(n.id, e)}
                            title="Mark as read"
                            className="p-1 text-slate-400 hover:text-emerald-600 transition-colors rounded hover:bg-emerald-50"
                          >
                            <Check className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="p-2.5 bg-slate-50/70 border-t border-slate-200/80 text-center text-[10px] text-slate-500 flex items-center justify-center space-x-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Broker Topic: <code className="font-mono text-slate-600 font-semibold">document.workflow.events</code></span>
          </div>
        </div>
      )}
    </div>
  );
};

