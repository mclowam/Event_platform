import { request, requestMultipart, buildUrl } from './base.js';

const EVENTS = 'events';

export async function getEvents(page = 1, size = 10) {
  const params = new URLSearchParams({ page, size });
  return request(`${EVENTS}?${params}`);
}

export async function getEvent(id) {
  return request(`${EVENTS}/${id}`);
}

/** URL for event image (use in <img src={...} />). */
export function getEventImageUrl(id) {
  return buildUrl(`${EVENTS}/${id}/image`);
}

/**
 * Create event (organizer/admin). Form fields: title, description, location, status_id, max_volunteers, start_time, end_time, file.
 */
export async function createEvent(formData) {
  return requestMultipart(EVENTS, formData, { method: 'POST' });
}
