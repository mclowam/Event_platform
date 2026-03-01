import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createEvent } from '../api/events.js';

export default function CreateEventPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({
    title: '',
    description: '',
    location: '',
    status_id: 1,
    max_volunteers: 10,
    start_time: '',
    end_time: '',
  });
  const [file, setFile] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: name === 'status_id' || name === 'max_volunteers' ? Number(value) : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const fd = new FormData();
      const start = form.start_time && !form.start_time.includes(':00:00') ? `${form.start_time}:00` : form.start_time;
      const end = form.end_time && !form.end_time.includes(':00:00') ? `${form.end_time}:00` : form.end_time;
      Object.entries(form).forEach(([k, v]) => {
        if (k === 'start_time') fd.append(k, start);
        else if (k === 'end_time') fd.append(k, end);
        else fd.append(k, v);
      });
      if (file) fd.append('file', file);
      await createEvent(fd);
      navigate('/events');
    } catch (err) {
      setError(err?.data?.detail || err?.message || 'Ошибка создания');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <h1 className="page-title">Создать событие</h1>
      {error && <div className="alert alert-error">{error}</div>}
      <form onSubmit={handleSubmit} className="form" style={{ maxWidth: '420px' }}>
        <label className="field">
          <span>Название</span>
          <input name="title" value={form.title} onChange={handleChange} required />
        </label>
        <label className="field">
          <span>Описание</span>
          <textarea name="description" value={form.description} onChange={handleChange} rows={3} />
        </label>
        <label className="field">
          <span>Место</span>
          <input name="location" value={form.location} onChange={handleChange} required />
        </label>
        <label className="field">
          <span>Статус (id)</span>
          <input name="status_id" type="number" value={form.status_id} onChange={handleChange} required />
        </label>
        <label className="field">
          <span>Макс. волонтёров</span>
          <input name="max_volunteers" type="number" value={form.max_volunteers} onChange={handleChange} min={0} />
        </label>
        <label className="field">
          <span>Начало (ISO)</span>
          <input name="start_time" type="datetime-local" value={form.start_time} onChange={handleChange} required />
        </label>
        <label className="field">
          <span>Конец (ISO)</span>
          <input name="end_time" type="datetime-local" value={form.end_time} onChange={handleChange} required />
        </label>
        <label className="field">
          <span>Изображение</span>
          <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} required />
        </label>
        <button className="btn primary" type="submit" disabled={loading}>
          {loading ? 'Создание…' : 'Создать'}
        </button>
      </form>
    </main>
  );
}
