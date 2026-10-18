/**
 * Centralized API configuration for AstroMind AI Frontend.
 * Points to the deployed Render backend by default, overridable via NEXT_PUBLIC_API_URL.
 */
export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL || "https://astromind-backend.onrender.com"
).replace(/\/+$/, "");

export function getApiUrl(path: string): string {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
}
