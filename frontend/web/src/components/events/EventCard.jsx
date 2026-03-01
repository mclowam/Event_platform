import { Link } from 'react-router-dom';
import { getEventImageUrl } from '../../api/events.js';

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' });
}

export default function EventCard({ event }) {
  const imageUrl = getEventImageUrl(event.id);

  return (
    <article className="card event-card">
      <Link to={`/events/${event.id}`} className="event-card-link">
        {event.image_url && (
          <div className="event-card-image">
            <img src={imageUrl} alt="" />
          </div>
        )}
        <h3 className="event-card-title">{event.title}</h3>
        <p className="event-card-meta">
          {event.location} · {formatDate(event.start_time)}
        </p>
        <p className="event-card-desc">{event.description?.slice(0, 120)}…</p>
      </Link>
    </article>
  );
}
