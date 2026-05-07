const LOCAL_API_FALLBACK = "http://localhost:8000";
const API_PREFIX = "/api/v1";

function normalizeBaseUrl(value) {
  const trimmed = (value || "").trim().replace(/\/$/, "");
  if (!trimmed) {
    return "";
  }
  if (trimmed.endsWith(API_PREFIX)) {
    return trimmed.slice(0, -API_PREFIX.length);
  }
  return trimmed;
}

function resolveApiBaseUrl() {
  const configuredBaseUrl = normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL);
  if (configuredBaseUrl) {
    return configuredBaseUrl;
  }

  if (typeof window !== "undefined") {
    const hostname = window.location.hostname;
    if (hostname === "localhost" || hostname === "127.0.0.1") {
      return LOCAL_API_FALLBACK;
    }
  }

  return "";
}

function buildUrl(path, params) {
  const baseUrl = resolveApiBaseUrl();
  if (!baseUrl) {
    throw new Error(
      "NEXT_PUBLIC_API_BASE_URL is not configured. Set it to your live backend URL before using the web app.",
    );
  }
  const url = new URL(`${baseUrl}${API_PREFIX}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    });
  }
  return url.toString();
}

async function parseResponse(response) {
  if (response.ok) {
    return response.json();
  }

  let message = "Request failed.";
  try {
    const payload = await response.json();
    message = payload.detail || payload.message || message;
  } catch {
    message = response.statusText || message;
  }
  throw new Error(message);
}

export async function getJson(path, params) {
  const response = await fetch(buildUrl(path, params), {
    cache: "no-store",
  });
  return parseResponse(response);
}

export async function postJson(path, body) {
  const response = await fetch(buildUrl(path), {
    method: "POST",
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  return parseResponse(response);
}

export async function postForm(path, formData) {
  const response = await fetch(buildUrl(path), {
    method: "POST",
    body: formData,
  });
  return parseResponse(response);
}

export const API_BASE_URL = resolveApiBaseUrl();
