import { User } from "@/types/auth";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Filters a list of users to find those created within a specific number of days.
 * @param {Array<User>} users - The array of user objects.
 * @param {number} daysAgo - The number of days to look back.
 * @returns {Array<User>} - The filtered array of recent users.
 */
export const getRecentUsers = (users: User[] | undefined, daysAgo = 7) => {
  // Return an empty array if the input isn't a valid array
  if (!Array.isArray(users)) {
    return [];
  }

  const thresholdDate = new Date();
  thresholdDate.setDate(thresholdDate.getDate() - daysAgo);

  return users.filter((user) => {
    const createdAt = new Date(user.created_at);
    return createdAt >= thresholdDate;
  });
};
