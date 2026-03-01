import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext.jsx';

export default function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [skills, setSkills] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { registerUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await registerUser({
        username,
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        phone: phone || undefined,
        skills: skills || undefined,
      });
      navigate('/', { replace: true });
    } catch (err) {
      setError(err?.data?.detail || (Array.isArray(err?.data) ? err.data.map((x) => x.msg).join(', ') : err?.message) || 'Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Регистрация</h2>
      {error && <div className="alert alert-error">{error}</div>}
      <form onSubmit={handleSubmit} className="form">
        <label className="field">
          <span>Имя пользователя</span>
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label className="field">
          <span>Email</span>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label className="field">
          <span>Пароль</span>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <label className="field">
          <span>Имя</span>
          <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
        </label>
        <label className="field">
          <span>Фамилия</span>
          <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} required />
        </label>
        <label className="field">
          <span>Телефон (необязательно)</span>
          <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} />
        </label>
        <label className="field">
          <span>Навыки (необязательно)</span>
          <input type="text" value={skills} onChange={(e) => setSkills(e.target.value)} />
        </label>
        <button className="btn primary" type="submit" disabled={loading}>
          {loading ? 'Загрузка...' : 'Зарегистрироваться'}
        </button>
      </form>
    </div>
  );
}
