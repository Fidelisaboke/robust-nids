import { User } from "@/types/auth";

interface ProfileTabProps {
  user: User | undefined;
}

export function ProfileTab({ user }: ProfileTabProps) {
  const fields = [
    { label: "First Name", value: user?.first_name || "" },
    { label: "Last Name", value: user?.last_name || "" },
    { label: "Email", value: user?.email || "" },
    { label: "Username", value: user?.username || "" },
    { label: "Department", value: user?.department || "" },
    { label: "Job Title", value: user?.job_title || "" },
  ];

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 space-y-6">
      <h2 className="text-2xl font-bold text-white">Profile Information</h2>

      <div className="grid md:grid-cols-2 gap-4">
        {fields.map((field) => (
          <div key={field.label}>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              {field.label}
            </label>
            <input
              type="text"
              value={field.value}
              readOnly
              className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
