import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getMyApplications } from '../api/applications.js';

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('ru-RU', { dateStyle: 'short' });
}

export default function MyApplicationsPage() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getMyApplications()
      .then((data) => { if (!cancelled) setList(Array.isArray(data) ? data : []); })
      .catch((err) => { if (!cancelled) setError(err?.message || 'Ошибка'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  return (
    <main className="page">
      <h1 className="page-title">Мои заявки</h1>
      <p className="page-subtitle">События, на которые вы подали заявку.</p>
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? (
        <p className="page-text">Загрузка…</p>
      ) : list.length === 0 ? (
        <p className="page-text">Нет заявок.</p>
      ) : (
        <ul className="applications-list">
          {list.map((app) => (
            <li key={app.id} className="card">
              <Link to={`/events/${app.event_id}`}>
                <strong>{app.event?.title ?? `Событие #${app.event_id}`}</strong>
              </Link>
              <span className="page-text">Подана: {formatDate(app.applied_at)}</span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
