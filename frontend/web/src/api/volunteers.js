import { request, getStoredTokens, buildUrl } from './base.js';

const VOLUNTEERS = 'volunteers';

/** Fetch QR as blob; use URL.createObjectURL(blob) for <img src={...} />. Requires auth header. */
export async function getMyQrBlob(eventId) {
  const tokens = getStoredTokens();
  const access = tokens?.access ?? tokens?.access_token;
  const url = buildUrl(`${VOLUNTEERS}/qr/${eventId}`);
  const res = await fetch(url, {
    headers: access ? { Authorization: `Bearer ${access}` } : {},
  });
  if (!res.ok) throw new Error('Failed to load QR');
  return res.blob();
}

export async function getMyHours() {
  return request(`${VOLUNTEERS}/hours`);
}
