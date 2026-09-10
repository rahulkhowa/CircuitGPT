"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "student" | "faculty" | "admin";
  avatar_url?: string;
  bio?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (accessToken: string, refreshToken: string, userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem("circuitgpt_access_token");
    const savedUser = localStorage.getItem("circuitgpt_user");

    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem("circuitgpt_access_token");
        localStorage.removeItem("circuitgpt_user");
      }
    }
    setIsLoading(false);
  }, []);

  const login = (accessToken: string, refreshToken: string, userData: User) => {
    setToken(accessToken);
    setUser(userData);
    localStorage.setItem("circuitgpt_access_token", accessToken);
    localStorage.setItem("circuitgpt_refresh_token", refreshToken);
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("circuitgpt_user", JSON.stringify(userData));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("circuitgpt_access_token");
    localStorage.removeItem("circuitgpt_refresh_token");
    localStorage.removeItem("access_token");
    localStorage.removeItem("circuitgpt_user");
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
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
