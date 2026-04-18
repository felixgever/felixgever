import { FormEvent, useState } from "react";
import type { CSSProperties } from "react";

import { createSubscription, fetchProjectEstimate } from "../api/billing";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useBillingPlans, useInvoices, useSubscriptions } from "../hooks/useBilling";
import { useProjects } from "../hooks/useProjects";
import type { ProjectCostEstimate } from "../types";
import { formatCurrencyIls, formatDate } from "../utils/format";

export function BillingPage() {
  const { data: plans, loading: loadingPlans, error: plansError } = useBillingPlans();
  const {
    data: subscriptions,
    loading: loadingSubscriptions,
    error: subscriptionsError,
    run: reloadSubscriptions,
  } = useSubscriptions();
  const { data: invoices, loading: loadingInvoices, error: invoicesError } = useInvoices();
  const { data: projects } = useProjects();

  const [planId, setPlanId] = useState<number | undefined>(undefined);
  const [projectId, setProjectId] = useState<number | undefined>(undefined);
  const [estimate, setEstimate] = useState<ProjectCostEstimate | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [estimateError, setEstimateError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onCreateSubscription(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!planId) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      await createSubscription({
        billing_plan_id: planId,
        project_id: projectId,
        status: "active",
      });
      await reloadSubscriptions();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to create subscription");
    } finally {
      setSubmitting(false);
    }
  }

  async function onEstimateProject(projectValue: number) {
    if (!projectValue) return;
    setEstimateError(null);
    try {
      const data = await fetchProjectEstimate(projectValue);
      setEstimate(data);
    } catch (err) {
      setEstimateError(err instanceof Error ? err.message : "Failed to estimate project");
    }
  }

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <h1>Billing & Subscriptions</h1>
      <article style={boxStyle}>
        <h3>Create subscription</h3>
        <form onSubmit={onCreateSubscription} style={{ display: "grid", gap: 8 }}>
          <label>
            Billing plan
            <select
              value={planId ?? ""}
              onChange={(event) => setPlanId(Number(event.target.value))}
              required
            >
              <option value="">Select plan</option>
              {(plans ?? []).map((plan) => (
                <option key={plan.id} value={plan.id}>
                  {plan.name} ({plan.plan_type}) - {formatCurrencyIls(plan.monthly_price_ils)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Optional project
            <select
              value={projectId ?? ""}
              onChange={(event) => {
                const rawValue = event.target.value;
                if (!rawValue) {
                  setProjectId(undefined);
                  setEstimate(null);
                  return;
                }
                const value = Number(rawValue);
                if (Number.isNaN(value)) {
                  setProjectId(undefined);
                  return;
                }
                setProjectId(value);
                void onEstimateProject(value);
              }}
            >
              <option value="">No project</option>
              {(projects ?? []).map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit" disabled={submitting}>
            {submitting ? "Creating..." : "Create subscription"}
          </button>
        </form>
        <ErrorState message={submitError} />
        <ErrorState message={estimateError} />
        {estimate ? (
          <p>
            Project estimate: {estimate.unit_count} units × {estimate.per_unit_price_ils}₪ ={" "}
            <strong>{formatCurrencyIls(estimate.estimated_total_ils)}</strong>
          </p>
        ) : null}
      </article>

      <article style={boxStyle}>
        <h3>Plans</h3>
        {loadingPlans ? <LoadingState /> : null}
        <ErrorState message={plansError} />
        <ul>
          {(plans ?? []).map((plan) => (
            <li key={plan.id}>
              {plan.name} | type: {plan.plan_type} | monthly:{" "}
              {formatCurrencyIls(plan.monthly_price_ils)} | per-unit:{" "}
              {formatCurrencyIls(plan.per_unit_price_ils)}
            </li>
          ))}
        </ul>
      </article>

      <article style={boxStyle}>
        <h3>Subscriptions</h3>
        {loadingSubscriptions ? <LoadingState /> : null}
        <ErrorState message={subscriptionsError} />
        <ul>
          {(subscriptions ?? []).map((subscription) => (
            <li key={subscription.id}>
              #{subscription.id} | status: {subscription.status} | plan:{" "}
              {subscription.billing_plan_id} | project: {subscription.project_id ?? "-"} | started:{" "}
              {formatDate(subscription.started_at)}
            </li>
          ))}
        </ul>
      </article>

      <article style={boxStyle}>
        <h3>Invoices</h3>
        {loadingInvoices ? <LoadingState /> : null}
        <ErrorState message={invoicesError} />
        <ul>
          {(invoices ?? []).map((invoice) => (
            <li key={invoice.id}>
              Invoice #{invoice.id} | {formatCurrencyIls(invoice.amount_ils)} | status:{" "}
              {invoice.status} | issued: {formatDate(invoice.issued_at)}
            </li>
          ))}
        </ul>
      </article>
    </section>
  );
}

const boxStyle: CSSProperties = {
  background: "#fff",
  borderRadius: 8,
  padding: 16,
};
