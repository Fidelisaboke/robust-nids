"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  Check,
  X,
  Mail,
  Building,
  Briefcase,
  Clock,
} from "lucide-react";
import {
  usePendingRegistrations,
  useApproveRegistration,
  useRejectRegistration,
} from "@/hooks/useUserManagement";
import { ConfirmActionDialog } from "@/components/admin/ConfirmActionDialog";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDistanceToNow } from "date-fns";

export default function PendingRegistrationsPage() {
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState(1);
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    action: "approve" | "reject" | null;
    registrationId: number | null;
    userName: string;
  }>({ open: false, action: null, registrationId: null, userName: "" });

  const { data: registrationsData, isLoading } = usePendingRegistrations(
    currentPage,
    20,
  );

  const approveMutation = useApproveRegistration();
  const rejectMutation = useRejectRegistration();

  const handleAction = async () => {
    if (!confirmDialog.registrationId) return;

    try {
      if (confirmDialog.action === "approve") {
        await approveMutation.mutateAsync(confirmDialog.registrationId);
      } else if (confirmDialog.action === "reject") {
        await rejectMutation.mutateAsync({
          id: confirmDialog.registrationId,
          reason: "Registration rejected by administrator",
        });
      }
      setConfirmDialog({
        open: false,
        action: null,
        registrationId: null,
        userName: "",
      });
    } catch (error) {
      // Error handling is done in the mutations
    }
  };

  const openConfirmDialog = (
    action: "approve" | "reject",
    registrationId: number,
    userName: string,
  ) => {
    setConfirmDialog({ open: true, action, registrationId, userName });
  };

  const getDialogContent = () => {
    switch (confirmDialog.action) {
      case "approve":
        return {
          title: "Approve Registration",
          description: `Are you sure you want to approve the registration for ${confirmDialog.userName}? They will receive an email notification and can access the system.`,
          confirmText: "Approve",
          variant: "default" as const,
        };
      case "reject":
        return {
          title: "Reject Registration",
          description: `Are you sure you want to reject the registration for ${confirmDialog.userName}? They will be notified of the rejection.`,
          confirmText: "Reject",
          variant: "destructive" as const,
        };
      default:
        return {
          title: "",
          description: "",
          confirmText: "",
          variant: "default" as const,
        };
    }
  };

  const dialogContent = getDialogContent();
  const isActionLoading = approveMutation.isPending || rejectMutation.isPending;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64 bg-slate-800" />
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-32 bg-slate-800" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center space-x-4">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-gray-400" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-white">
              Pending Registrations
            </h1>
            <p className="text-gray-400 mt-2">
              Review and approve new user registration requests
            </p>
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="bg-slate-800/50 border border-orange-500/20 rounded-xl p-6"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-orange-500/10 rounded-lg">
              <Clock className="w-6 h-6 text-orange-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">
                {registrationsData?.total || 0}
              </p>
              <p className="text-sm text-gray-400">Pending Requests</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Registrations List */}
      {registrationsData && registrationsData?.items.length > 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="space-y-4"
        >
          {registrationsData.items.map((registration) => (
            <div
              key={registration.id}
              className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-emerald-500/30 transition-colors"
            >
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                {/* User Info */}
                <div className="flex-1">
                  <div className="flex items-start space-x-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white font-semibold text-lg">
                      {registration.first_name?.[0]}
                      {registration.last_name?.[0]}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white">
                        {registration.first_name} {registration.last_name}
                      </h3>
                      <div className="flex flex-wrap gap-4 mt-2">
                        <div className="flex items-center space-x-2 text-sm text-gray-400">
                          <Mail className="w-4 h-4" />
                          <span>{registration.email}</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-400">
                          <Building className="w-4 h-4" />
                          <span>{registration.department}</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-400">
                          <Briefcase className="w-4 h-4" />
                          <span>{registration.job_title}</span>
                        </div>
                        <div className="flex items-center space-x-2 text-sm text-gray-400">
                          <Clock className="w-4 h-4" />
                          <span>
                            {formatDistanceToNow(
                              new Date(registration.created_at),
                              { addSuffix: true },
                            )}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                  <button
                    onClick={() =>
                      openConfirmDialog(
                        "reject",
                        registration.id,
                        `${registration.first_name} ${registration.last_name}`,
                      )
                    }
                    disabled={isActionLoading}
                    className="flex items-center space-x-2 px-4 py-2.5 bg-red-600 hover:bg-red-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4" />
                    <span>Reject</span>
                  </button>
                  <button
                    onClick={() =>
                      openConfirmDialog(
                        "approve",
                        registration.id,
                        `${registration.first_name} ${registration.last_name}`,
                      )
                    }
                    disabled={isActionLoading}
                    className="flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                  >
                    <Check className="w-4 h-4" />
                    <span>Approve</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-center py-12 bg-slate-800/50 border border-slate-700 rounded-xl"
        >
          <p className="text-gray-400 text-lg">No pending registrations</p>
          <p className="text-gray-500 text-sm mt-2">
            All registration requests have been processed
          </p>
        </motion.div>
      )}

      {/* Pagination */}
      {registrationsData && registrationsData.pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-900 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            Previous
          </button>
          <span className="text-gray-400">
            Page {currentPage} of {registrationsData.pages}
          </span>
          <button
            onClick={() =>
              setCurrentPage((p) => Math.min(registrationsData.pages, p + 1))
            }
            disabled={currentPage === registrationsData.pages}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-900 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            Next
          </button>
        </div>
      )}

      {/* Confirmation Dialog */}
      <ConfirmActionDialog
        open={confirmDialog.open}
        onOpenChange={(open) =>
          setConfirmDialog({
            open,
            action: confirmDialog.action,
            registrationId: confirmDialog.registrationId,
            userName: confirmDialog.userName,
          })
        }
        onConfirm={handleAction}
        title={dialogContent.title}
        description={dialogContent.description}
        confirmText={dialogContent.confirmText}
        variant={dialogContent.variant}
        isLoading={isActionLoading}
      />
    </div>
  );
}
