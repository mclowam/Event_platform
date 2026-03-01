import { useState, useEffect } from 'react';
import { getEvents } from '../api/events.js';
import EventCard from '../components/events/EventCard.jsx';

export default function EventsPage() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const size = 10;

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getEvents(page, size)
      .then((data) => {
        if (!cancelled) setList(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        if (!cancelled) setError(err?.message || 'Ошибка загрузки');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [page]);

  return (
    <main className="page">
      <h1 className="page-title">События</h1>
      <p className="page-subtitle">Список мероприятий для волонтёров.</p>
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? (
        <p className="page-text">Загрузка…</p>
      ) : (
        <div className="events-grid">
          {list.length === 0 ? (
            <p className="page-text">Нет событий.</p>
          ) : (
            list.map((ev) => <EventCard key={ev.id} event={ev} />)
          )}
        </div>
      )}
      {list.length >= size && (
        <div style={{ marginTop: '1rem' }}>
          <button className="btn primary" onClick={() => setPage((p) => p + 1)}>
            Ещё
          </button>
        </div>
      )}
    </main>
  );
}
