import { apiClient } from "./client";
import type { Resident } from "../types";

export async function fetchResidents(projectId: number): Promise<Resident[]> {
  const { data } = await apiClient.get<Resident[]>("/residents", {
    params: { project_id: projectId },
  });
  return data;
}

export async function createResident(payload: {
  project_id: number;
  unit_id?: number;
  full_name: string;
  phone?: string;
  email?: string;
  id_number?: string;
  is_primary_contact?: boolean;
}): Promise<Resident> {
  const { data } = await apiClient.post<Resident>("/residents", payload);
  return data;
}
