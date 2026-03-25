import { useEffect, useState } from "react";
import { fetchDashboardData } from "../services/api";
import type { DashboardData } from "../types/analytics";

interface DashboardState {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
}

export function useDashboardData(handle: string) {
  const [state, setState] = useState<DashboardState>({
    data: null,
    loading: true,
    error: null
  });
  const [reloadCount, setReloadCount] = useState(0);

  useEffect(() => {
    let cancelled = false;

    if (!handle.trim()) {
      setState({
        data: null,
        loading: false,
        error: "Enter a Codeforces handle to continue."
      });
      return () => {
        cancelled = true;
      };
    }

    setState((currentState) => ({
      data: currentState.data,
      loading: true,
      error: null
    }));

    fetchDashboardData(handle)
      .then((data) => {
        if (!cancelled) {
          setState({ data, loading: false, error: null });
        }
      })
      .catch((error: Error) => {
        if (!cancelled) {
          setState({
            data: null,
            loading: false,
            error: error.message || "Unable to load analytics right now."
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [handle, reloadCount]);

  return {
    ...state,
    reload: () => setReloadCount((currentCount) => currentCount + 1)
  };
}
