import { useState } from 'react';
import { attendanceByQr, attendanceByEmail, getAttendanceStats } from '../api/organizers.js';
import QrScanner from '../components/QrScanner.jsx';

export default function OrganizerAttendancePage() {
  const [qrToken, setQrToken] = useState('');
  const [email, setEmail] = useState('');
  const [eventId, setEventId] = useState('');
  const [statsEventId, setStatsEventId] = useState('');
  const [stats, setStats] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleScanResult = async (token) => {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await attendanceByQr(token);
      setResult(data);
    } catch (err) {
      setError(err?.data?.detail || err?.message || 'Ошибка при отметке');
    } finally {
      setLoading(false);
    }
  };

  const handleQrSubmit = async (e) => {
    e.preventDefault();
    if (!qrToken.trim()) return;
    await handleScanResult(qrToken.trim());
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await attendanceByEmail(email, Number(eventId));
      setResult(data);
    } catch (err) {
      setError(err?.data?.detail || err?.message || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadStats = async (e) => {
    e.preventDefault();
    if (!statsEventId) return;
    setError(null);
    setLoading(true);
    try {
      const data = await getAttendanceStats(Number(statsEventId));
      setStats(data);
    } catch (err) {
      setError(err?.data?.detail || err?.message || 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  const resultMessage = result && (
    <div className="alert alert-success">
      {result.message || 'Отметка засчитана.'}
      {result.current_state && <span> Статус: {result.current_state}</span>}
      {result.hours_worked != null && <span> Часы: {result.hours_worked}</span>}
    </div>
  );

  return (
    <main className="page">
      <h1 className="page-title">Посещаемость</h1>
      <p className="page-subtitle">Сканируйте QR волонтёра камерой или введите токен вручную. Доступно организаторам и администраторам.</p>
      {error && <div className="alert alert-error">{error}</div>}
      {resultMessage}

      <div className="card card-scanner">
        <h2>Сканирование QR волонтёра</h2>
        <p className="page-text" style={{ marginBottom: '1rem' }}>Наведите камеру на QR-код волонтёра. После успешной отметки сканирование остановится.</p>
        <QrScanner onScan={handleScanResult} />
        {loading && <p className="page-text">Отправка отметки…</p>}
        <hr className="qr-scanner-divider" />
        <p className="page-text" style={{ marginBottom: '0.5rem' }}>Или вставьте токен из QR вручную:</p>
        <form onSubmit={handleQrSubmit} className="form form-inline">
          <input
            className="qr-token-input"
            value={qrToken}
            onChange={(e) => setQrToken(e.target.value)}
            placeholder="Вставьте токен из QR"
            disabled={loading}
          />
          <button className="btn primary" type="submit" disabled={loading}>Отметить по токену</button>
        </form>
      </div>

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h2>Отметка по email</h2>
        <p className="page-text" style={{ marginBottom: '1rem' }}>Если волонтёр не может показать QR, введите его email и ID события.</p>
        <form onSubmit={handleEmailSubmit} className="form">
          <label className="field">
            <span>Email волонтёра</span>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label className="field">
            <span>ID события</span>
            <input type="number" value={eventId} onChange={(e) => setEventId(e.target.value)} placeholder="Например: 1" required />
          </label>
          <button className="btn primary" type="submit" disabled={loading}>Отметить</button>
        </form>
      </div>

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h2>Статистика по событию</h2>
        <form onSubmit={handleLoadStats} className="form">
          <label className="field">
            <span>ID события</span>
            <input type="number" value={statsEventId} onChange={(e) => setStatsEventId(e.target.value)} placeholder="Например: 1" />
          </label>
          <button className="btn primary" type="submit" disabled={loading}>Загрузить</button>
        </form>
        {stats && (
          <div className="stats-grid">
            <span>Зарегистрировано: <strong>{stats.registered}</strong></span>
            <span>На месте: <strong>{stats.checked_in}</strong></span>
            <span>Завершили: <strong>{stats.completed}</strong></span>
            <span>Отсутствуют: <strong>{stats.absent}</strong></span>
          </div>
        )}
      </div>
    </main>
  );
}
