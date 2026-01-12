/**
 * Shared API base URL resolver for REST + WebSocket clients.
 */

export const getApiBaseUrl = (): string => {
  // Always check for environment variable first (works in both dev and prod)
  const envUrl = import.meta.env.VITE_API_BASE_URL;

  // In production without env var, try to detect if we're on the same domain
  // If backend is on different domain, this will fail - user must set VITE_API_BASE_URL
  if (import.meta.env.PROD) {
    // Try to use same origin (assumes proxy or same domain)
    // Note: This assumes backend is proxied through Vercel or on same domain
    const origin = window.location.origin;
    const forceSameOrigin =
      import.meta.env.VITE_FORCE_SAME_ORIGIN === "true" ||
      window.location.hostname.endsWith("eieconcierge.com");
    if (forceSameOrigin) {
      return `${origin}/api/v1`;
    }
  }

  if (envUrl) {
    return envUrl;
  }

  // In development, use localhost
  return "http://localhost:8000/api/v1";
};

export const getWebSocketBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_WS_BASE_URL;
  if (envUrl) {
    return envUrl;
  }

  if (import.meta.env.PROD && window.location.hostname.endsWith("eieconcierge.com")) {
    // Prefer API subdomain for WebSocket because Vercel rewrites do not proxy WS.
    return "https://api.eieconcierge.com";
  }

  const apiBaseUrl = getApiBaseUrl();
  // Strip /api/v1 if present, keep scheme/host.
  return apiBaseUrl.replace(/\/api\/v1$/, "");
};
