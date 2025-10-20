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
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const router = useRouter();

  // Initialize auth state on mount
  useEffect(() => {
    const token = sessionStorage.getItem("access_token");
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
        sessionStorage.clear();
        setIsAuthenticated(false);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = (
    accessToken: string,
    refreshToken: string,
    userData?: User,
  ) => {
    sessionStorage.setItem("access_token", accessToken);
    sessionStorage.setItem("refresh_token", refreshToken);
    if (userData) setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    sessionStorage.removeItem("mfa_challenge_token");
    setUser(null);
    setIsAuthenticated(false);
    router.replace("/login");
  };

  const saveMfaChallengeToken = (token: string) => {
    sessionStorage.setItem("mfa_challenge_token", token);
  };

  const getMfaChallengeToken = (): string | null => {
    return sessionStorage.getItem("mfa_challenge_token");
  };

  const clearMfaChallengeToken = () => {
    sessionStorage.removeItem("mfa_challenge_token");
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
