"use client";

import { useState } from "react";
import { SettingsLayout } from "./components/SettingsLayout";
import { SettingsTabs } from "./components/SettingsTabs";
import { ProfileTab } from "./components/tabs/ProfileTab";
import { SecurityTab } from "./components/tabs/SecurityTab";
import { NotificationsTab } from "./components/tabs/NotificationsTab";
import { DisableMfaDialog } from "./components/DisableMfaDialog";
import { User, Bell, Lock } from "lucide-react";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

const tabs = [
  { id: "profile", label: "Profile", icon: User },
  { id: "security", label: "Security", icon: Lock },
  { id: "notifications", label: "Notifications", icon: Bell },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("security");
  const [disableMfaDialogOpen, setDisableMfaDialogOpen] = useState(false);
  const { user, isLoading: userLoading } = useAuth();

  if (userLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    );
  }

  const renderActiveTab = () => {
    switch (activeTab) {
      case "profile":
        return <ProfileTab user={user} />;
      case "security":
        return <SecurityTab user={user} />;
      case "notifications":
        return <NotificationsTab user={user} />;
      default:
        return <SecurityTab user={user} />;
    }
  };

  return (
    <>
      <SettingsLayout
        title="Settings"
        description="Manage your account settings and preferences"
      >
        <SettingsTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
          tabs={tabs}
        >
          {renderActiveTab()}
        </SettingsTabs>
      </SettingsLayout>

      <DisableMfaDialog
        open={disableMfaDialogOpen}
        onOpenChange={setDisableMfaDialogOpen}
      />
    </>
  );
}
