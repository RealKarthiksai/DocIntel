import React, { createContext, useContext, useState, useEffect } from "react";
import api from "../api/client";

export interface User {
  id: number;
  email: string;
  role: string;
  tenant_id: string;
  permissions: string[];
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, pass: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchUser = async () => {
      const storedToken = localStorage.getItem("token");
      if (storedToken) {
        try {
          const res = await api.get("/auth/me");
          setUser({
            id: res.data.id,
            email: res.data.email,
            role: res.data.role_name,
            tenant_id: res.data.tenant_id,
            permissions: res.data.permissions
          });
        } catch (err) {
          localStorage.removeItem("token");
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    fetchUser();
  }, [token]);

  const login = async (email: string, pass: string) => {
    const res = await api.post("/auth/login", { email, password: pass });
    const { access_token, user_id, role, tenant_id, permissions } = res.data;
    localStorage.setItem("token", access_token);
    setToken(access_token);
    setUser({
      id: user_id,
      email,
      role,
      tenant_id,
      permissions
    });
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
