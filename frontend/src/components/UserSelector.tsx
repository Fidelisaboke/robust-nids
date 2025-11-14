import { useState, useMemo, useEffect, useRef } from "react";
import { Search, User, X, Loader2 } from "lucide-react";
import { useUsers } from "@/hooks/useUserManagement";

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  department: string;
  job_title: string;
}

interface UserSelectorProps {
  selectedUserId: number | null;
  onSelect: (userId: number, user: User) => void;
  onClear?: () => void;
  disabled?: boolean;
}

export function UserSelector({
  selectedUserId,
  onSelect,
  onClear,
  disabled = false,
}: UserSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const scrollRef = useRef<HTMLDivElement>(null);
  const pageSize = 20;

  // Fetch users with pagination
  const { data: usersData, isLoading } = useUsers({
    page: currentPage,
    size: pageSize,
  });

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery]);

  // Filter users based on search query
  const filteredUsers = useMemo(() => {
    if (!usersData?.items) return [];

    const query = searchQuery.toLowerCase();
    if (!query) return usersData.items;

    return usersData.items.filter(
      (user: User) =>
        user.username.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query) ||
        `${user.first_name} ${user.last_name}`.toLowerCase().includes(query) ||
        user.department?.toLowerCase().includes(query) ||
        user.job_title?.toLowerCase().includes(query),
    );
  }, [usersData, searchQuery]);

  // Get selected user details - need to fetch if not in current page
  const { data: selectedUserData } = useUsers({
    page: 1,
    size: 100, // Fetch more to find selected user
  });

  const selectedUser = useMemo(() => {
    if (!selectedUserId) return null;

    // First check current page data
    let user = usersData?.items.find((u: User) => u.id === selectedUserId);

    // If not found, check the larger fetch
    if (!user && selectedUserData?.items) {
      user = selectedUserData.items.find((u: User) => u.id === selectedUserId);
    }

    return user || null;
  }, [selectedUserId, usersData, selectedUserData]);

  const handleSelect = (user: User) => {
    onSelect(user.id, user);
    setIsOpen(false);
    setSearchQuery("");
    setCurrentPage(1);
  };

  const handleClear = () => {
    onClear?.();
    setSearchQuery("");
    setCurrentPage(1);
  };

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const element = e.currentTarget;
    const isBottom =
      element.scrollHeight - element.scrollTop <= element.clientHeight + 50;

    // Load more when near bottom and there are more pages
    if (isBottom && usersData && currentPage < usersData.pages && !isLoading) {
      setCurrentPage((prev) => prev + 1);
    }
  };

  const hasMorePages = usersData ? currentPage < usersData.pages : false;

  return (
    <div className="relative">
      <label className="block text-sm font-medium text-gray-300 mb-2">
        Assign to User
      </label>

      {/* Selected User Display / Dropdown Trigger */}
      <div className="relative">
        <div
          onClick={() => !disabled && setIsOpen(!isOpen)}
          className={`w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-left text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${
            disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
          }`}
          role="button"
          tabIndex={disabled ? -1 : 0}
          onKeyDown={(e) => {
            if (!disabled && (e.key === "Enter" || e.key === " ")) {
              e.preventDefault();
              setIsOpen(!isOpen);
            }
          }}
        >
          {selectedUser ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 min-w-0 flex-1">
                <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-blue-400" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-white truncate">
                    {selectedUser.first_name} {selectedUser.last_name}
                  </p>
                  <p className="text-xs text-gray-400 truncate">
                    {selectedUser.email}
                  </p>
                </div>
              </div>
              {onClear && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClear();
                  }}
                  className="p-1 hover:bg-slate-700 rounded transition-colors flex-shrink-0 ml-2"
                >
                  <X className="w-4 h-4 text-gray-400" />
                </button>
              )}
            </div>
          ) : (
            <span className="text-gray-500">Select a user...</span>
          )}
        </div>

        {/* Dropdown Menu */}
        {isOpen && (
          <div className="absolute z-[60] mt-2 w-full bg-slate-800 border border-slate-700 rounded-lg shadow-2xl overflow-hidden">
            {/* Search Input - Sticky at top */}
            <div className="sticky top-0 p-3 border-b border-slate-700 bg-slate-800 z-10">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search users..."
                  className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                />
              </div>
            </div>

            {/* User List - Scrollable with better height */}
            <div
              ref={scrollRef}
              onScroll={handleScroll}
              className="overflow-y-auto overscroll-contain"
              style={{
                maxHeight: "min(320px, 50vh)",
                scrollbarWidth: "thin",
                scrollbarColor: "#475569 #1e293b",
              }}
            >
              {isLoading && currentPage === 1 ? (
                <div className="p-8 text-center">
                  <Loader2 className="w-6 h-6 text-blue-400 animate-spin mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">Loading users...</p>
                </div>
              ) : filteredUsers.length === 0 ? (
                <div className="p-8 text-center">
                  <User className="w-12 h-12 text-gray-600 mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">No users found</p>
                  {searchQuery && (
                    <p className="text-gray-500 text-xs mt-1">
                      Try a different search term
                    </p>
                  )}
                </div>
              ) : (
                <>
                  <div className="py-1">
                    {filteredUsers.map((user: User) => (
                      <button
                        key={user.id}
                        type="button"
                        onClick={() => handleSelect(user)}
                        className={`w-full px-4 py-3 text-left hover:bg-slate-700 transition-colors focus:bg-slate-700 focus:outline-none ${
                          selectedUserId === user.id
                            ? "bg-slate-700/50 border-l-2 border-blue-500"
                            : ""
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                            <User className="w-5 h-5 text-blue-400" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white">
                              {user.first_name} {user.last_name}
                            </p>
                            <p className="text-xs text-gray-400 truncate">
                              {user.email}
                            </p>
                            {(user.job_title || user.department) && (
                              <p className="text-xs text-gray-500 mt-0.5 truncate">
                                {user.job_title}
                                {user.job_title && user.department && " • "}
                                {user.department}
                              </p>
                            )}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>

                  {/* Load More Indicator */}
                  {hasMorePages && (
                    <div className="sticky bottom-0 p-3 text-center border-t border-slate-700 bg-slate-800/95 backdrop-blur-sm">
                      {isLoading ? (
                        <div className="flex items-center justify-center space-x-2">
                          <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                          <span className="text-sm text-gray-400">
                            Loading more...
                          </span>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setCurrentPage((prev) => prev + 1)}
                          className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          Load more users
                        </button>
                      )}
                    </div>
                  )}

                  {/* Pagination Info */}
                  {usersData && (
                    <div className="sticky bottom-0 px-4 py-2 text-xs text-gray-500 text-center border-t border-slate-700 bg-slate-800">
                      Showing {filteredUsers.length} of {usersData.total} users
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Click outside to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-[55]"
          onClick={() => {
            setIsOpen(false);
            setSearchQuery("");
            setCurrentPage(1);
          }}
        />
      )}
    </div>
  );
}
