import { useState, useEffect } from 'react';
import { getMyHours } from '../api/volunteers.js';

export default function VolunteerHoursPage() {
  const [hours, setHours] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getMyHours()
      .then((data) => { if (!cancelled) setHours(data?.total_hours ?? 0); })
      .catch((err) => { if (!cancelled) setError(err?.message || 'Ошибка'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  return (
    <main className="page">
      <h1 className="page-title">Мои часы</h1>
      <p className="page-subtitle">Общее количество волонтёрских часов.</p>
      {error && <div className="alert alert-error">{error}</div>}
      {loading ? (
        <p className="page-text">Загрузка…</p>
      ) : (
        <div className="card">
          <p className="page-text"><strong>Всего часов: {hours}</strong></p>
        </div>
      )}
    </main>
  );
}
