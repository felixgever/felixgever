import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { getCurrentUser, login as apiLogin, register as apiRegister } from "../api/auth";
import { getAccessToken, setAccessToken } from "../api/client";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: {
    email: string;
    full_name: string;
    password: string;
    organization_name?: string;
    roles?: string[];
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function bootstrapAuth() {
      const token = getAccessToken();
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        setAccessToken(null);
      } finally {
        setLoading(false);
      }
    }
    void bootstrapAuth();
  }, []);

  async function login(email: string, password: string) {
    setLoading(true);
    try {
      const token = await apiLogin(email, password);
      setAccessToken(token.access_token);
      const me = await getCurrentUser();
      setUser(me);
    } finally {
      setLoading(false);
    }
  }

  async function register(payload: {
    email: string;
    full_name: string;
    password: string;
    organization_name?: string;
    roles?: string[];
  }) {
    setLoading(true);
    try {
      await apiRegister(payload);
      await login(payload.email, payload.password);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    setAccessToken(null);
    setUser(null);
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      loading,
      login,
      register,
      logout,
    }),
    [loading, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
