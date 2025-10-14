"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import type { User } from "@/types/auth";
import { authApi } from "@/lib/api/authApi";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  login: (accessToken: string, refreshToken: string, user?: User) => void;
  logout: () => void;
  saveMfaChallengeToken: (token: string) => void;
  getMfaChallengeToken: () => string | null;
  clearMfaChallengeToken: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    const token = localStorage.getItem("access_token");
    return !!token;
  });
  const router = useRouter();

  // Initialize auth state on mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setIsAuthenticated(false);
      setIsLoading(false);
      return;
    }

    // Fetch user profile
    authApi
      .getCurrentUser()
      .then((data) => {
        setUser(data);
        setIsAuthenticated(true);
      })
      .catch(() => {
        localStorage.clear();
        setIsAuthenticated(false);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = (
    accessToken: string,
    refreshToken: string,
    userData?: User,
  ) => {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    if (userData) setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("mfa_challenge_token");
    setUser(null);
    router.push("/login");
  };

  const saveMfaChallengeToken = (token: string) => {
    localStorage.setItem("mfa_challenge_token", token);
  };

  const getMfaChallengeToken = (): string | null => {
    return localStorage.getItem("mfa_challenge_token");
  };

  const clearMfaChallengeToken = () => {
    localStorage.removeItem("mfa_challenge_token");
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    setUser,
    login,
    logout,
    saveMfaChallengeToken,
    getMfaChallengeToken,
    clearMfaChallengeToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
};
