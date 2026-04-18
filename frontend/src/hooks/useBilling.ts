import { useCallback } from "react";

import {
  fetchBillingPlans,
  fetchInvoices,
  fetchSubscriptions,
} from "../api/billing";
import { useAsync } from "./useAsync";

export function useBillingPlans() {
  const fetcher = useCallback(() => fetchBillingPlans(), []);
  return useAsync(fetcher, true);
}

export function useSubscriptions() {
  const fetcher = useCallback(() => fetchSubscriptions(), []);
  return useAsync(fetcher, true);
}

export function useInvoices(subscriptionId?: number) {
  const fetcher = useCallback(() => fetchInvoices(subscriptionId), [subscriptionId]);
  return useAsync(fetcher, true);
}
