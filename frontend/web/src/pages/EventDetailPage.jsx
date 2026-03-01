import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getEvent, getEventImageUrl } from '../api/events.js';
import { applyForEvent, cancelApplication, getMyApplications } from '../api/applications.js';
import { getMyQrBlob } from '../api/volunteers.js';
import { useAuth } from '../context/AuthContext.jsx';

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('ru-RU', { dateStyle: 'short', timeStyle: 'short' });
}

export default function EventDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [event, setEvent] = useState(null);
  const [myApplicationEventIds, setMyApplicationEventIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [qrBlobUrl, setQrBlobUrl] = useState(null);

  useEffect(() => {
    let cancelled = false;
    if (!id) return;
    getEvent(id)
      .then((data) => { if (!cancelled) setEvent(data); })
      .catch((err) => { if (!cancelled) setError(err?.message || 'Ошибка'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [id]);

  useEffect(() => {
    if (!isAuthenticated) return;
    let cancelled = false;
    getMyApplications()
      .then((apps) => {
        if (!cancelled && Array.isArray(apps)) {
          setMyApplicationEventIds(new Set(apps.map((a) => a.event_id)));
        }
      })
      .catch(() => {});
    return () => { cancelled = true; };
  }, [isAuthenticated]);

  const applied = event && myApplicationEventIds.has(event.id);

  const loadQr = () => {
    if (!event?.id) return;
    setQrBlobUrl(null);
    getMyQrBlob(event.id)
      .then((blob) => setQrBlobUrl(URL.createObjectURL(blob)))
      .catch(() => setError('Не удалось загрузить QR'));
  };

  useEffect(() => {
    return () => { if (qrBlobUrl) URL.revokeObjectURL(qrBlobUrl); };
  }, [qrBlobUrl]);

  const handleApply = async () => {
    if (!user || !event) return;
    setActionLoading(true);
    try {
      await applyForEvent(event.id);
      setMyApplicationEventIds((s) => new Set([...s, event.id]));
    } catch (err) {
      setError(err?.data?.detail || err?.message || 'Ошибка');
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!event) return;
    setActionLoading(true);
    try {
      await cancelApplication(event.id);
      setMyApplicationEventIds((s) => {
        const next = new Set(s);
        next.delete(event.id);
        return next;
      });
    } catch (err) {
      setError(err?.data?.detail || err?.message || 'Ошибка');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <main className="page"><p className="page-text">Загрузка…</p></main>;
  if (error && !event) return <main className="page"><div className="alert alert-error">{error}</div></main>;
  if (!event) return null;

  return (
    <main className="page">
      <button type="button" className="btn small secondary" onClick={() => navigate(-1)} style={{ marginBottom: '1rem' }}>
        ← Назад
      </button>
      <div className="card event-detail">
        {event.image_url && (
          <div className="event-detail-image">
            <img src={getEventImageUrl(event.id)} alt="" />
          </div>
        )}
        <h1 className="page-title">{event.title}</h1>
        <p className="page-subtitle">{event.location} · {formatDate(event.start_time)} — {formatDate(event.end_time)}</p>
        <p className="page-text">{event.description}</p>
        <p className="page-text">Макс. волонтёров: {event.max_volunteers}. Статус: {event.status?.name}</p>
        {error && <div className="alert alert-error">{error}</div>}
        {isAuthenticated && (
          <div style={{ marginTop: '1rem' }}>
            {applied ? (
              <>
                <button className="btn danger" onClick={handleCancel} disabled={actionLoading}>
                  Отменить заявку
                </button>
                <button type="button" className="btn small" onClick={loadQr} style={{ marginLeft: '0.5rem' }}>
                  Показать мой QR
                </button>
                {qrBlobUrl && <img src={qrBlobUrl} alt="QR" style={{ display: 'block', marginTop: '0.5rem', maxWidth: 160 }} />}
              </>
            ) : (
              <button className="btn primary" onClick={handleApply} disabled={actionLoading}>
                {actionLoading ? '…' : 'Подать заявку'}
              </button>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
