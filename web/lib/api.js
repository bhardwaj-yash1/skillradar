const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const API_PREFIX = "/api/v1";

function buildUrl(path, params) {
  const url = new URL(`${API_BASE_URL}${API_PREFIX}${path}`);
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

export { API_BASE_URL };
