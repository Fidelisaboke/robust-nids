"use client";

import { Pagination } from "@/components/Pagination";
import {
  downloadReport,
  useDeleteReport,
  useReports,
} from "@/hooks/useReportManagement";
import { ReportStatus } from "@/types/enums";
import { motion } from "framer-motion";
import {
  AlertCircle,
  Calendar,
  Clock,
  Download,
  FileText,
  Filter,
  Loader2,
  Plus,
  Trash,
} from "lucide-react";
import { useState } from "react";
import { ReportGenerationDialog } from "./components/ReportGenerationDialog";
import { DeleteConfirmationDialog } from "@/components/dialogs/DeleteConfirmationDialog";
import { useDebounce } from "@/hooks/useDebounce";

export default function ReportsPage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [reportToDelete, setReportToDelete] = useState<number | null>(null);
  const debouncedSearchQuery = useDebounce(searchFilter, 500);
  const deleteReport = useDeleteReport();

  const {
    data: reportsData,
    isLoading,
    error,
  } = useReports({
    page: currentPage,
    size: 10,
    search: debouncedSearchQuery,
    status: statusFilter,
  });

  const getStatusColor = (status: ReportStatus) => {
    switch (status) {
      case ReportStatus.READY:
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case ReportStatus.PENDING:
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      case ReportStatus.RUNNING:
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      case ReportStatus.FAILED:
        return "bg-red-500/20 text-red-400 border-red-500/30";
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30";
    }
  };

  const getStatusIcon = (status: ReportStatus) => {
    switch (status) {
      case ReportStatus.READY:
        return <Download className="w-4 h-4" />;
      case ReportStatus.PENDING:
      case ReportStatus.RUNNING:
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case ReportStatus.FAILED:
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const handleDownload = async (reportId: number, reportTitle: string) => {
    await downloadReport(reportId, reportTitle);
  };

  const handleDelete = async (reportId: number) => {
    await deleteReport.mutateAsync(reportId);
    setIsDeleteDialogOpen(false);
    setReportToDelete(null);
  };

  const stats = [
    {
      label: "Total Reports",
      value: reportsData?.total.toString() || "0",
      icon: FileText,
      color: "text-blue-400",
    },
    {
      label: "Ready",
      value:
        reportsData?.items
          .filter((r) => r.status === ReportStatus.READY)
          .length.toString() || "0",
      icon: Download,
      color: "text-green-400",
    },
    {
      label: "Pending",
      value:
        reportsData?.items
          .filter(
            (r) =>
              r.status === ReportStatus.PENDING ||
              r.status === ReportStatus.RUNNING,
          )
          .length.toString() || "0",
      icon: Clock,
      color: "text-yellow-400",
    },
    {
      label: "Failed",
      value:
        reportsData?.items
          .filter((r) => r.status === ReportStatus.FAILED)
          .length.toString() || "0",
      icon: AlertCircle,
      color: "text-red-400",
    },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white">Reports & Analytics</h1>
        <p className="text-gray-400 mt-2">
          Generate and access security reports
        </p>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <Icon className={`w-8 h-8 ${stat.color}`} />
              </div>
              <p className="text-3xl font-bold text-white mb-2">{stat.value}</p>
              <p className="text-sm text-gray-400">{stat.label}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Generate New Report */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-linear-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20 rounded-xl p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white mb-2">
              Generate New Report
            </h2>
            <p className="text-gray-400">
              Create custom security reports with specific date ranges and
              filters
            </p>
          </div>
          <button
            onClick={() => setIsDialogOpen(true)}
            className="px-6 py-3 bg-linear-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Create Report</span>
          </button>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-4"
      >
        <div className="flex items-center space-x-4">
          <Filter className="w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search reports..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="flex-1 px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value={ReportStatus.READY}>Ready</option>
            <option value={ReportStatus.PENDING}>Pending</option>
            <option value={ReportStatus.RUNNING}>Running</option>
            <option value={ReportStatus.FAILED}>Failed</option>
          </select>
        </div>
      </motion.div>

      {/* Reports List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
      >
        <h2 className="text-xl font-bold text-white mb-6">Recent Reports</h2>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-12 text-red-400">
            <AlertCircle className="w-6 h-6 mr-2" />
            <span>Failed to load reports</span>
          </div>
        ) : !reportsData?.items.length ? (
          <div className="text-center py-12 text-gray-400">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No reports found. Create your first report to get started!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {reportsData.items.map((report, index) => (
              <motion.div
                key={report.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-slate-900/50 rounded-lg p-5 hover:bg-slate-900 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    <div className="p-3 bg-blue-500/10 rounded-lg">
                      <FileText className="w-6 h-6 text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3 mb-2 flex-wrap">
                        <h3 className="text-lg font-semibold text-white">
                          {report.title}
                        </h3>
                        <span
                          className={`text-xs font-semibold px-3 py-1 rounded-full border flex items-center space-x-1 ${getStatusColor(report.status)}`}
                        >
                          {getStatusIcon(report.status)}
                          <span className="capitalize">{report.status}</span>
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-4 text-sm mb-2">
                        <div className="flex items-center space-x-2">
                          <Calendar className="w-4 h-4 text-gray-500" />
                          <span className="text-gray-400">
                            {new Date(
                              report.parameters.start_date,
                            ).toLocaleDateString()}{" "}
                            -{" "}
                            {new Date(
                              report.parameters.end_date,
                            ).toLocaleDateString()}
                          </span>
                        </div>
                        {report.parameters.severity && (
                          <div className="flex items-center space-x-2">
                            <span className="text-gray-500">Severity:</span>
                            <span className="text-gray-400 capitalize">
                              {report.parameters.severity}
                            </span>
                          </div>
                        )}
                        {report.parameters.search && (
                          <div className="flex items-center space-x-2">
                            <span className="text-gray-500">Filter:</span>
                            <span className="text-gray-400">
                              {report.parameters.search}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="text-xs text-gray-500">
                        Created by {report.owner.username} on{" "}
                        {new Date(report.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    {report.status === ReportStatus.READY && (
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() =>
                            handleDownload(report.id, report.title)
                          }
                          className="p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-lg transition-colors"
                          title="Download Report"
                        >
                          <Download className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => {
                            setReportToDelete(report.id);
                            setIsDeleteDialogOpen(true);
                          }}
                          className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
                          title="Delete Report"
                        >
                          <Trash className="w-5 h-5" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {reportsData && reportsData.pages > 1 && (
          <div className="mt-6">
            <Pagination
              currentPage={currentPage}
              totalPages={reportsData.pages}
              onPageChange={setCurrentPage}
              totalItems={reportsData.total}
              itemsPerPage={10}
            />
          </div>
        )}
      </motion.div>

      {/* Report Generation Dialog */}
      <ReportGenerationDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmationDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={() =>
          reportToDelete !== null && handleDelete(reportToDelete)
        }
        itemName={
          reportsData?.items.find((report) => report.id === reportToDelete)
            ?.title || ""
        }
        isDeleting={deleteReport.isPending}
      />
    </div>
  );
}
