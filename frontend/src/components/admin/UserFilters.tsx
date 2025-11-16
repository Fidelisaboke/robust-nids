import React, { useEffect, useState } from "react";
import { Search, Filter, X, Download } from "lucide-react";
import { UserListParams } from "@/lib/api/usersApi";
import { useDebounce } from "@/hooks/useDebounce";

interface UserFiltersProps {
  onFilterChange: (filters: UserListParams) => void;
  onExport: () => void;
  isExporting?: boolean;
}

export const UserFilters: React.FC<UserFiltersProps> = ({
  onFilterChange,
  onExport,
  isExporting = false,
}) => {
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");
  const [status, setStatus] = useState("");
  const [verification, setVerification] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  const debouncedSearch = useDebounce(search, 500);

  const handleSearchChange = (value: string) => {
    setSearch(value);
  };

  const applyFilters = (overrides: Partial<UserListParams> = {}) => {
    const filters: UserListParams = {
      search: debouncedSearch || undefined,
      role: role || undefined,
      is_active:
        status === "active" ? true : status === "inactive" ? false : undefined,
      email_verified:
        verification === "verified"
          ? true
          : verification === "unverified"
            ? false
            : undefined,
      ...overrides,
    };
    onFilterChange(filters);
  };

  const clearFilters = () => {
    setSearch("");
    setRole("");
    setStatus("");
    setVerification("");
    onFilterChange({});
  };

  // Use effect to apply filters when debouncedSearch changes (ignore warning)
  useEffect(() => {
    applyFilters();
  }, [debouncedSearch, role, status, verification]); // eslint-disable-line react-hooks/exhaustive-deps

  const hasActiveFilters = search || role || status || verification;

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name, email, or username..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
          />
        </div>

        {/* Filter Toggle */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-gray-300 hover:bg-slate-700 transition-colors"
        >
          <Filter className="w-5 h-5" />
          <span>Filters</span>
          {hasActiveFilters && (
            <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">
              Active
            </span>
          )}
        </button>

        {/* Export Button */}
        <button
          onClick={onExport}
          disabled={isExporting}
          className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
        >
          <Download className="w-5 h-5" />
          <span>{isExporting ? "Exporting..." : "Export"}</span>
        </button>
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
          {/* Role Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Role
            </label>
            <select
              value={role}
              onChange={(e) => {
                setRole(e.target.value);
                applyFilters({ role: e.target.value || undefined });
              }}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="analyst">Security Analyst</option>
              <option value="manager">Security Manager</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Account Status
            </label>
            <select
              value={status}
              onChange={(e) => {
                setStatus(e.target.value);
                applyFilters({
                  is_active:
                    e.target.value === "active"
                      ? true
                      : e.target.value === "inactive"
                        ? false
                        : undefined,
                });
              }}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          {/* Verification Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Email Verification
            </label>
            <select
              value={verification}
              onChange={(e) => {
                setVerification(e.target.value);
                applyFilters({
                  email_verified:
                    e.target.value === "verified"
                      ? true
                      : e.target.value === "unverified"
                        ? false
                        : undefined,
                });
              }}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="">All</option>
              <option value="verified">Verified</option>
              <option value="unverified">Unverified</option>
            </select>
          </div>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <div className="md:col-span-3 flex justify-end">
              <button
                onClick={clearFilters}
                className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
                <span>Clear all filters</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
