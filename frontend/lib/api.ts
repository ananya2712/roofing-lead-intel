import createClient from "openapi-fetch";
import type { components, paths } from "./api-types";

// Same-origin calls. next.config.mjs forwards /api/v1 to the Flask backend.
export const api = createClient<paths>({ baseUrl: "/api/v1" });

type S = components["schemas"];
export type ProspectSummary = S["ProspectSummary"];
export type ProspectDetail = S["ProspectDetail"];
export type ProspectStats = S["ProspectStats"];
export type LeadSummary = S["LeadSummary"];
export type Overview = S["Overview"];
export type LeadStatus = S["LeadStatus"];
export type Tier = S["Tier"];
export type Directory = S["Directory"];
export type ApiError = S["Error"];

export const LEAD_STATUSES: LeadStatus[] = ["new", "contacted", "qualified", "dismissed"];

/** Turn an API error body into a message for the user. */
export function errorMessage(error: unknown, fallback: string): string {
  const e = error as Partial<ApiError> | undefined;
  return e?.error?.message ?? fallback;
}

/** Throw on an error response so callers can use one try/catch. */
export async function unwrap<T>(
  call: Promise<{ data?: T; error?: unknown; response: Response }>,
  fallback: string,
): Promise<T> {
  let result: { data?: T; error?: unknown; response: Response };
  try {
    result = await call;
  } catch (e) {
    // A network failure throws a browser message such as "Failed to fetch".
    // Keep aborts as they are (useLoad ignores them) and show the user the clear fallback text.
    if (e instanceof DOMException && e.name === "AbortError") throw e;
    throw new Error(fallback);
  }
  const { data, error, response } = result;
  if (error !== undefined || data === undefined) {
    const err = new Error(errorMessage(error, fallback)) as Error & { status?: number; body?: unknown };
    err.status = response.status;
    err.body = error;
    throw err;
  }
  return data;
}
