import { apiClient } from "./client";
import type {
  DeveloperBid,
  DocumentItem,
  MessageItem,
  Plan,
  Signature,
  WorkflowStage,
} from "../types";

export async function fetchSignatures(projectId: number): Promise<Signature[]> {
  const { data } = await apiClient.get<Signature[]>("/signatures", {
    params: { project_id: projectId },
  });
  return data;
}

export async function fetchWorkflowStages(projectId: number): Promise<WorkflowStage[]> {
  const { data } = await apiClient.get<WorkflowStage[]>("/workflow/stages", {
    params: { project_id: projectId },
  });
  return data;
}

export async function fetchBids(projectId: number): Promise<DeveloperBid[]> {
  const { data } = await apiClient.get<DeveloperBid[]>("/bids", {
    params: { project_id: projectId },
  });
  return data;
}

export async function fetchPlans(projectId: number): Promise<Plan[]> {
  const { data } = await apiClient.get<Plan[]>("/plans", {
    params: { project_id: projectId },
  });
  return data;
}

export async function fetchDocuments(projectId: number): Promise<DocumentItem[]> {
  const { data } = await apiClient.get<DocumentItem[]>("/documents", {
    params: { project_id: projectId },
  });
  return data;
}

export async function fetchMessages(projectId: number): Promise<MessageItem[]> {
  const { data } = await apiClient.get<MessageItem[]>("/messages", {
    params: { project_id: projectId },
  });
  return data;
}
