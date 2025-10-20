import { User } from "@/types/auth";

interface NotificationsTabProps {
  user: User | undefined;
}

export function NotificationsTab({ user }: NotificationsTabProps) {
  const notificationSettings = [
    {
      key: "email",
      label: "Email Notifications",
      description: "Receive alerts via email",
      checked: user?.preferences?.notifications?.email || false,
    },
    {
      key: "browser",
      label: "Browser Notifications",
      description: "Get push notifications in your browser",
      checked: user?.preferences?.notifications?.browser || false,
    },
    {
      key: "critical_alerts",
      label: "Critical Alerts",
      description: "High-priority security alerts",
      checked: user?.preferences?.notifications?.critical_alerts || false,
    },
  ];

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 space-y-6">
      <h2 className="text-2xl font-bold text-white">
        Notification Preferences
      </h2>

      <div className="space-y-4">
        {notificationSettings.map((setting) => (
          <div
            key={setting.key}
            className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg"
          >
            <div>
              <p className="text-white font-medium">{setting.label}</p>
              <p className="text-sm text-gray-400">{setting.description}</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={setting.checked}
                readOnly
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        ))}
      </div>
    </div>
  );
}
