import { apiClient } from "./client";
import type { Project, Unit } from "../types";

export async function fetchProjects(): Promise<Project[]> {
  const { data } = await apiClient.get<Project[]>("/projects");
  return data;
}

export async function fetchProject(projectId: number): Promise<Project> {
  const { data } = await apiClient.get<Project>(`/projects/${projectId}`);
  return data;
}

export async function createProject(payload: {
  name: string;
  city: string;
  address?: string;
  description?: string;
  per_unit_price_ils?: number;
}): Promise<Project> {
  const { data } = await apiClient.post<Project>("/projects", payload);
  return data;
}

export async function addUnit(
  projectId: number,
  payload: {
    unit_number: string;
    floor?: number;
    existing_area_sqm?: number;
  },
): Promise<Unit> {
  const { data } = await apiClient.post<Unit>(`/projects/${projectId}/units`, {
    project_id: projectId,
    ...payload,
  });
  return data;
}
