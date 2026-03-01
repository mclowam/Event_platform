import { API_BASE_URL, STORAGE_KEYS } from '../config/index.js';

export function getStoredTokens() {
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.authTokens);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setStoredTokens(tokens) {
  if (tokens) {
    localStorage.setItem(STORAGE_KEYS.authTokens, JSON.stringify(tokens));
  } else {
    localStorage.removeItem(STORAGE_KEYS.authTokens);
  }
}

export function clearStoredTokens() {
  localStorage.removeItem(STORAGE_KEYS.authTokens);
}

function getAuthHeaders() {
  const tokens = getStoredTokens();
  const access = tokens?.access ?? tokens?.access_token;
  if (!access) return {};
  return { Authorization: `Bearer ${access}` };
}


export function buildUrl(path) {
  const p = path.startsWith('/') ? path : '/' + path;
  return (API_BASE_URL + p).replace(/([^:]\/)\/+/g, '$1');
}

export async function request(path, options = {}) {
  const { method = 'GET', body, headers = {} } = options;
  const url = buildUrl(path);

  const res = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...headers,
    },
    body: body != null ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const err = new Error('API error');
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}


export async function requestForm(path, params, options = {}) {
  const { method = 'POST', headers = {} } = options;
  const body = new URLSearchParams(params).toString();
  const url = buildUrl(path);

  const res = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      ...getAuthHeaders(),
      ...headers,
    },
    body,
  });

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const err = new Error('API error');
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}


export async function requestMultipart(path, formData, options = {}) {
  const { method = 'POST', headers = {} } = options;
  const url = buildUrl(path);

  const res = await fetch(url, {
    method,
    headers: {
      ...getAuthHeaders(),
      ...headers,
    },
    body: formData,
  });

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const err = new Error('API error');
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}
