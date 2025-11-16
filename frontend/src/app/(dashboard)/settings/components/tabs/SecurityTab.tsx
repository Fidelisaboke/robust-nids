"use client";

import { useState } from "react";
import { User } from "@/types/auth";
import { MfaSection } from "./security/MfaSection";
import { PasswordSection } from "./security/PasswordSection";
import { SessionsSection } from "./security/SessionsSection";
import { DisableMfaDialog } from "../DisableMfaDialog";

interface SecurityTabProps {
  user: User | null;
}

export function SecurityTab({ user }: SecurityTabProps) {
  const [disableMfaDialogOpen, setDisableMfaDialogOpen] = useState(false);

  return (
    <div className="space-y-6">
      <MfaSection
        user={user}
        onDisableMfa={() => setDisableMfaDialogOpen(true)}
      />
      <PasswordSection />
      <SessionsSection user={user} />
      <DisableMfaDialog
        open={disableMfaDialogOpen}
        onOpenChange={setDisableMfaDialogOpen}
      />
    </div>
  );
}
