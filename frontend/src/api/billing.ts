import { apiClient } from "./client";
import type { BillingPlan, Invoice, ProjectCostEstimate, Subscription } from "../types";

export async function fetchBillingPlans(): Promise<BillingPlan[]> {
  const { data } = await apiClient.get<BillingPlan[]>("/billing/plans");
  return data;
}

export async function fetchSubscriptions(): Promise<Subscription[]> {
  const { data } = await apiClient.get<Subscription[]>("/subscriptions");
  return data;
}

export async function createSubscription(payload: {
  billing_plan_id: number;
  user_id?: number;
  project_id?: number;
  status?: string;
  auto_renew?: boolean;
  add_ons_json?: string;
}): Promise<Subscription> {
  const { data } = await apiClient.post<Subscription>("/subscriptions", payload);
  return data;
}

export async function fetchInvoices(
  subscriptionId?: number,
): Promise<Invoice[]> {
  const { data } = await apiClient.get<Invoice[]>("/billing/invoices", {
    params: subscriptionId ? { subscription_id: subscriptionId } : undefined,
  });
  return data;
}

export async function fetchProjectEstimate(
  projectId: number,
): Promise<ProjectCostEstimate> {
  const { data } = await apiClient.get<ProjectCostEstimate>(
    `/billing/projects/${projectId}/estimate`,
  );
  return data;
}
