import { request } from './base.js';

const ORGANIZERS = 'organizers';

/** Check-in/out by QR token (body: { qr_token }). */
export async function attendanceByQr(qrToken) {
  return request(`${ORGANIZERS}/attendance/qr`, {
    method: 'POST',
    body: { qr_token: qrToken },
  });
}

/** Manual check-in by email (body: { email, event_id }). */
export async function attendanceByEmail(email, eventId) {
  return request(`${ORGANIZERS}/attendance/email`, {
    method: 'POST',
    body: { email, event_id: eventId },
  });
}

export async function getAttendanceStats(eventId) {
  return request(`${ORGANIZERS}/attendance/stats?event_id=${eventId}`);
}
