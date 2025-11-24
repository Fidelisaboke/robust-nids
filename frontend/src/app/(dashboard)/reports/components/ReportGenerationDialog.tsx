import { useState } from "react";
import { motion } from "framer-motion";
import { Loader2, X } from "lucide-react";
import {
  useCreateReport,
  ReportCreateRequest,
} from "@/hooks/useReportManagement";
import { AlertSeverity, AlertStatus } from "@/types/enums";

// Report Generation Dialog Component
export function ReportGenerationDialog({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const [formData, setFormData] = useState<ReportCreateRequest>({
    title: "",
    start_date: "",
    end_date: "",
    severity: "",
    status: "",
    search: "",
  });

  const createReport = useCreateReport();

  const handleSubmit = () => {
    if (!formData.title || !formData.start_date || !formData.end_date) {
      return;
    }

    // Convert naive local datetime to UTC ISO string
    const start_date_utc = new Date(formData.start_date).toISOString();
    const end_date_utc = new Date(formData.end_date).toISOString();

    // Clean up form data - remove empty optional fields
    const cleanedData: ReportCreateRequest = {
      title: formData.title,
      start_date: start_date_utc,
      end_date: end_date_utc,
    };

    if (formData.severity) cleanedData.severity = formData.severity;
    if (formData.status) cleanedData.status = formData.status;
    if (formData.search) cleanedData.search = formData.search;

    createReport.mutate(cleanedData, {
      onSuccess: () => {
        onClose();
        setFormData({
          title: "",
          start_date: "",
          end_date: "",
          severity: "",
          status: "",
          search: "",
        });
      },
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-slate-800 border border-slate-700 rounded-xl p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Generate New Report</h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Report Title *
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) =>
                setFormData({ ...formData, title: e.target.value })
              }
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Q4 Security Analysis"
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Start Date *
              </label>
              <input
                type="datetime-local"
                required
                value={formData.start_date}
                onChange={(e) =>
                  setFormData({ ...formData, start_date: e.target.value })
                }
                className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                End Date *
              </label>
              <input
                type="datetime-local"
                required
                value={formData.end_date}
                onChange={(e) =>
                  setFormData({ ...formData, end_date: e.target.value })
                }
                className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Severity (Optional)
              </label>
              <select
                value={formData.severity}
                onChange={(e) =>
                  setFormData({ ...formData, severity: e.target.value })
                }
                className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Severities</option>
                <option value={AlertSeverity.LOW}>Low</option>
                <option value={AlertSeverity.MEDIUM}>Medium</option>
                <option value={AlertSeverity.HIGH}>High</option>
                <option value={AlertSeverity.CRITICAL}>Critical</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Status (Optional)
              </label>
              <select
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value })
                }
                className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value={AlertStatus.ACTIVE}>Active</option>
                <option value={AlertStatus.INVESTIGATING}>Investigating</option>
                <option value={AlertStatus.ACKNOWLEDGED}>Acknowledged</option>
                <option value={AlertStatus.RESOLVED}>Resolved</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Search Filter (Optional)
            </label>
            <input
              type="text"
              value={formData.search}
              onChange={(e) =>
                setFormData({ ...formData, search: e.target.value })
              }
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Bruteforce, SQL Injection"
            />
          </div>

          <div className="flex items-center justify-end space-x-3 pt-4">
            <button
              onClick={onClose}
              className="px-6 py-2 text-gray-300 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={
                createReport.isPending ||
                !formData.title ||
                !formData.start_date ||
                !formData.end_date
              }
              className="px-6 py-2 bg-linear-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {createReport.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <span>Generate Report</span>
              )}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
