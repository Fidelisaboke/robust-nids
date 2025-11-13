import { useState } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, Check, Trash2, UserPlus, X } from "lucide-react";
import {
  useAssignAlert,
  useAcknowledgeAlert,
  useResolveAlert,
  useDeleteAlert,
} from "@/hooks/useAlertManagement";
import { Alert } from "@/lib/api/alertsApi";
import { toast } from "sonner";
import { normalizeError } from "@/lib/api/apiClient";

interface AlertActionsDialogProps {
  alert: Alert;
  onClose: () => void;
}

export function AlertActionsDialog({
  alert,
  onClose,
}: AlertActionsDialogProps) {
  const [activeTab, setActiveTab] = useState<
    "assign" | "acknowledge" | "resolve" | "delete"
  >("assign");
  const [userId, setUserId] = useState("");
  const [notes, setNotes] = useState("");

  const assignMutation = useAssignAlert();
  const acknowledgeMutation = useAcknowledgeAlert();
  const resolveMutation = useResolveAlert();
  const deleteMutation = useDeleteAlert();
  const router = useRouter();

  const handleAssign = async () => {
    if (!userId) {
      toast.error("Please enter a user ID");
      return;
    }

    try {
      await assignMutation.mutateAsync({
        id: alert.id,
        data: { user_id: parseInt(userId) },
      });
      toast.success("Alert assigned successfully");
      onClose();
    } catch (error) {
      const normalizedError = normalizeError(error);
      toast.error(normalizedError.message || "Failed to assign alert");
    }
  };

  const handleAcknowledge = async () => {
    try {
      await acknowledgeMutation.mutateAsync(alert.id);
      toast.success("Alert acknowledged");
      onClose();
    } catch (error) {
      const normalizedError = normalizeError(error);
      toast.error(normalizedError.message || "Failed to acknowledge alert");
    }
  };

  const handleResolve = async () => {
    if (!notes.trim()) {
      toast.error("Please provide resolution notes");
      return;
    }

    // Notes should be 10 characters long at a minimum
    if (notes.trim().length < 10) {
      toast.error("Resolution notes must be at least 10 characters long");
      return;
    }

    try {
      await resolveMutation.mutateAsync({
        id: alert.id,
        data: { notes },
      });
      toast.success("Alert resolved successfully");
      onClose();
    } catch (error) {
      const normalizedError = normalizeError(error);
      toast.error(normalizedError.message || "Failed to resolve alert");
    }
  };

  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(alert.id);
      toast.success("Alert deleted successfully");
      onClose();
      router.push("/alerts");
    } catch (error) {
      const normalizedError = normalizeError(error);
      toast.error(normalizedError.message || "Failed to delete alert");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-md mx-4 shadow-2xl">
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-xl font-bold text-white">Alert Actions</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          <div className="flex space-x-2 mb-6">
            <button
              onClick={() => setActiveTab("assign")}
              className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === "assign"
                  ? "bg-blue-500 text-white"
                  : "bg-slate-700 text-gray-400 hover:bg-slate-600"
              }`}
            >
              <UserPlus className="w-4 h-4 inline-block mr-2" />
              Assign
            </button>
            <button
              onClick={() => setActiveTab("acknowledge")}
              className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === "acknowledge"
                  ? "bg-blue-500 text-white"
                  : "bg-slate-700 text-gray-400 hover:bg-slate-600"
              }`}
            >
              <AlertTriangle className="w-4 h-4 inline-block mr-2" />
              Ack
            </button>
            <button
              onClick={() => setActiveTab("resolve")}
              className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === "resolve"
                  ? "bg-blue-500 text-white"
                  : "bg-slate-700 text-gray-400 hover:bg-slate-600"
              }`}
            >
              <Check className="w-4 h-4 inline-block mr-2" />
              Resolve
            </button>
            <button
              onClick={() => setActiveTab("delete")}
              className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === "delete"
                  ? "bg-red-500 text-white"
                  : "bg-slate-700 text-gray-400 hover:bg-slate-600"
              }`}
            >
              <Trash2 className="w-4 h-4 inline-block mr-2" />
              Delete
            </button>
          </div>

          {activeTab === "assign" && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  User ID
                </label>
                {/* TODO: Replace with user search dropdown */}
                <input
                  type="number"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  placeholder="Enter user ID"
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <button
                onClick={handleAssign}
                disabled={assignMutation.isPending}
                className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {assignMutation.isPending ? "Assigning..." : "Assign Alert"}
              </button>
            </div>
          )}

          {activeTab === "acknowledge" && (
            <div className="space-y-4">
              <p className="text-gray-400 text-sm">
                Acknowledge this alert to mark it as reviewed.
              </p>
              <button
                onClick={handleAcknowledge}
                disabled={acknowledgeMutation.isPending}
                className="w-full px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {acknowledgeMutation.isPending
                  ? "Acknowledging..."
                  : "Acknowledge Alert"}
              </button>
            </div>
          )}

          {activeTab === "resolve" && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Resolution Notes
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Enter resolution notes..."
                  rows={4}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>
              <button
                onClick={handleResolve}
                disabled={resolveMutation.isPending}
                className="w-full px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {resolveMutation.isPending ? "Resolving..." : "Resolve Alert"}
              </button>
            </div>
          )}

          {activeTab === "delete" && (
            <div className="space-y-4">
              <p className="text-gray-400 text-sm">
                Are you sure you want to delete this alert? This action cannot
                be undone.
              </p>
              <button
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
                className="w-full px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {deleteMutation.isPending ? "Deleting..." : "Delete Alert"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
