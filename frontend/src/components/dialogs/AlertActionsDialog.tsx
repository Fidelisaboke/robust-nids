import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  Check,
  Trash2,
  UserPlus,
  X,
  UserCheck,
} from "lucide-react";
import {
  useAssignAlert,
  useAcknowledgeAlert,
  useResolveAlert,
  useDeleteAlert,
} from "@/hooks/useAlertManagement";
import { Alert } from "@/lib/api/alertsApi";
import { toast } from "sonner";
import { normalizeError } from "@/lib/api/apiClient";
import { UserSelector } from "@/components/UserSelector";
import { useAuth } from "@/contexts/AuthContext";

interface AlertActionsDialogProps {
  alert: Alert;
  onClose: () => void;
}

export function AlertActionsDialog({
  alert,
  onClose,
}: AlertActionsDialogProps) {
  const { user: currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState<
    "assign" | "acknowledge" | "resolve" | "delete"
  >("assign");
  const [selectedUserId, setSelectedUserId] = useState<number | null>(
    alert.assigned_to_id,
  );
  const [notes, setNotes] = useState("");

  const assignMutation = useAssignAlert();
  const acknowledgeMutation = useAcknowledgeAlert();
  const resolveMutation = useResolveAlert();
  const deleteMutation = useDeleteAlert();
  const router = useRouter();

  const handleAssign = async () => {
    if (!selectedUserId) {
      toast.error("Please select a user");
      return;
    }

    try {
      await assignMutation.mutateAsync({
        id: alert.id,
        data: { user_id: selectedUserId },
      });
      toast.success("Alert assigned successfully");
      onClose();
    } catch (error) {
      const normalizedError = normalizeError(error);
      toast.error(normalizedError.message || "Failed to assign alert");
    }
  };

  const handleSelfAssign = async () => {
    if (!currentUser) {
      toast.error("User not authenticated");
      return;
    }

    try {
      await assignMutation.mutateAsync({
        id: alert.id,
        data: { user_id: currentUser.id },
      });
      toast.success("Alert assigned to you");
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-xl w-full max-w-lg shadow-2xl max-h-[85vh] flex flex-col">
        {/* Header - Fixed */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-xl font-bold text-white">Alert Actions</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Buttons - Fixed, Grid Layout */}
        <div className="grid grid-cols-2 gap-3 p-4 border-b border-slate-700">
          <button
            onClick={() => setActiveTab("assign")}
            className={`px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center space-x-2 ${
              activeTab === "assign"
                ? "bg-blue-500 text-white shadow-lg shadow-blue-500/20"
                : "bg-slate-700 text-gray-400 hover:bg-slate-600"
            }`}
          >
            <UserPlus className="w-4 h-4" />
            <span>Assign</span>
          </button>
          <button
            onClick={() => setActiveTab("acknowledge")}
            className={`px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center space-x-2 ${
              activeTab === "acknowledge"
                ? "bg-yellow-500 text-white shadow-lg shadow-yellow-500/20"
                : "bg-slate-700 text-gray-400 hover:bg-slate-600"
            }`}
          >
            <AlertTriangle className="w-4 h-4" />
            <span>Acknowledge</span>
          </button>
          <button
            onClick={() => setActiveTab("resolve")}
            className={`px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center space-x-2 ${
              activeTab === "resolve"
                ? "bg-green-500 text-white shadow-lg shadow-green-500/20"
                : "bg-slate-700 text-gray-400 hover:bg-slate-600"
            }`}
          >
            <Check className="w-4 h-4" />
            <span>Resolve</span>
          </button>
          <button
            onClick={() => setActiveTab("delete")}
            className={`px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center space-x-2 ${
              activeTab === "delete"
                ? "bg-red-500 text-white shadow-lg shadow-red-500/20"
                : "bg-slate-700 text-gray-400 hover:bg-slate-600"
            }`}
          >
            <Trash2 className="w-4 h-4" />
            <span>Delete</span>
          </button>
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === "assign" && (
            <div className="space-y-4">
              {/* Self-Assign Quick Action */}
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                <p className="text-sm text-gray-300 mb-3">
                  Assign this alert to yourself for investigation
                </p>
                <button
                  onClick={handleSelfAssign}
                  disabled={assignMutation.isPending}
                  className="w-full px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  <UserCheck className="w-4 h-4" />
                  <span>
                    {assignMutation.isPending ? "Assigning..." : "Assign to Me"}
                  </span>
                </button>
              </div>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-700"></div>
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-2 bg-slate-800 text-gray-400">
                    OR ASSIGN TO ANOTHER USER
                  </span>
                </div>
              </div>

              {/* User Selector */}
              <UserSelector
                selectedUserId={selectedUserId}
                onSelect={(userId) => setSelectedUserId(userId)}
                onClear={() => setSelectedUserId(null)}
                disabled={assignMutation.isPending}
              />

              <button
                onClick={handleAssign}
                disabled={assignMutation.isPending || !selectedUserId}
                className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {assignMutation.isPending ? "Assigning..." : "Assign Alert"}
              </button>
            </div>
          )}

          {activeTab === "acknowledge" && (
            <div className="space-y-4">
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
                <p className="text-sm text-gray-300">
                  Acknowledge this alert to mark it as reviewed. This indicates
                  you&apos;ve seen the alert and are aware of the threat.
                </p>
              </div>
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
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <p className="text-sm text-gray-300">
                  Mark this alert as resolved and document how the threat was
                  handled.
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Resolution Notes
                  <span className="text-gray-500 text-xs ml-2">
                    (min. 10 characters)
                  </span>
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Describe how the threat was resolved..."
                  rows={4}
                  className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {notes.length} characters
                </p>
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
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-red-400 font-medium text-sm mb-1">
                      Warning: This action cannot be undone
                    </p>
                    <p className="text-gray-400 text-sm">
                      Deleting this alert will permanently remove all associated
                      data, including assignment history and model analysis.
                    </p>
                  </div>
                </div>
              </div>
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
