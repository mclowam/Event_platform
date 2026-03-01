import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

function HomePage() {
    const { user } = useAuth();
    return (
        <main className="page">
            <h1 className="page-title">Платформа событий</h1>
            <p className="page-subtitle">
                Мероприятия, расписания и управление событиями. Перейдите в <Link to="/events">События</Link>, чтобы увидеть список.
            </p>

            {!user ? (
                <p className="page-text">
                    Войдите или зарегистрируйтесь через меню вверху, чтобы подавать заявки и видеть свои часы.
                </p>
            ) : (
                <div className="card">
                    <h2>Добро пожаловать, {user?.email}!</h2>
                    <p className="page-text">
                        Ваша роль: {user?.role}. Перейдите в «События» или «Мои заявки».
                    </p>
                </div>
            )}
        </main>
    );
}

export default HomePage;

