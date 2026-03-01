import { request } from './base.js';

const APPLICATIONS = 'applications';

export async function getMyApplications() {
  return request(APPLICATIONS);
}

export async function applyForEvent(eventId) {
  return request(APPLICATIONS, { method: 'POST', body: { event_id: eventId } });
}

export async function cancelApplication(eventId) {
  return request(`${APPLICATIONS}/${eventId}`, { method: 'DELETE' });
}
