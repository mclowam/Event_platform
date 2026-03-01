import { request, requestForm, setStoredTokens, getStoredTokens } from './base.js';

const AUTH = 'auth';

function normalizeTokens(data) {
  if (!data) return null;
  return {
    access: data.access_token ?? data.access,
    refresh: data.refresh_token ?? data.refresh,
  };
}

export async function login(usernameOrEmail, password) {
  const data = await requestForm(`${AUTH}/login`, {
    username: usernameOrEmail,
    password,
  });
  const tokens = normalizeTokens(data);
  if (tokens) setStoredTokens(tokens);
  return tokens;
}

export async function register(payload) {
  return request(`${AUTH}/register`, { method: 'POST', body: payload });
}

export async function refreshTokens() {
  const stored = getStoredTokens();
  const refresh = stored?.refresh ?? stored?.refresh_token;
  if (!refresh) throw new Error('No refresh token');
  const data = await request(`${AUTH}/refresh`, {
    method: 'POST',
    body: { refresh_token: refresh },
  });
  const tokens = normalizeTokens(data);
  if (tokens) setStoredTokens(tokens);
  return tokens;
}

export async function getMe() {
  return request(`${AUTH}/me`);
}
