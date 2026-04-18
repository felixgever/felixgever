import { useCallback } from "react";

import { fetchProjects } from "../api/projects";
import { useAsync } from "./useAsync";

export function useProjects() {
  const fetcher = useCallback(() => fetchProjects(), []);
  return useAsync(fetcher, true);
}
