import { useCallback } from "react";

import { fetchResidents } from "../api/residents";
import { useAsync } from "./useAsync";

export function useResidents(projectId?: number) {
  const fetcher = useCallback(() => {
    if (!projectId) {
      return Promise.resolve([]);
    }
    return fetchResidents(projectId);
  }, [projectId]);

  return useAsync(fetcher, Boolean(projectId));
}
