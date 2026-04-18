import { apiClient } from "./client";
import type { TokenResponse, User } from "../types";

export async function login(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);
  const { data } = await apiClient.post<TokenResponse>("/auth/login", body, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  return data;
}

export async function register(payload: {
  email: string;
  full_name: string;
  password: string;
  organization_name?: string;
  roles?: string[];
}): Promise<User> {
  const { data } = await apiClient.post<User>("/auth/register", payload);
  return data;
}

export async function getCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
}
