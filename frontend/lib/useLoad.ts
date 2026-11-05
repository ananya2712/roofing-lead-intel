"use client";
import { useCallback, useEffect, useRef, useState } from "react";

type State<T> = { data: T | null; error: string | null; loading: boolean };

/**
 * Load data for the current inputs. A newer request cancels the older one,
 * and a late response from an older request is ignored.
 */
export function useLoad<T>(loader: (signal: AbortSignal) => Promise<T>, key: string) {
  const [state, setState] = useState<State<T>>({ data: null, error: null, loading: true });
  const seq = useRef(0);
  const loaderRef = useRef(loader);
  loaderRef.current = loader;

  const run = useCallback(() => {
    const id = ++seq.current;
    const ctrl = new AbortController();
    setState((s) => ({ ...s, loading: true, error: null }));
    loaderRef
      .current(ctrl.signal)
      .then((data) => {
        if (id === seq.current) setState({ data, error: null, loading: false });
      })
      .catch((err: unknown) => {
        if (id !== seq.current || ctrl.signal.aborted) return;
        const message = err instanceof Error ? err.message : "The data could not be loaded.";
        setState((s) => ({ ...s, error: message, loading: false }));
      });
    return ctrl;
  }, []);

  useEffect(() => {
    const ctrl = run();
    return () => ctrl.abort();
  }, [key, run]);

  const setData = useCallback((updater: (d: T | null) => T | null) => {
    setState((s) => ({ ...s, data: updater(s.data) }));
  }, []);

  return { ...state, reload: run, setData };
}
