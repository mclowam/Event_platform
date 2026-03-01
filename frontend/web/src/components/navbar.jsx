import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function Navbar() {
  const { user, logout, isOrganizerOrAdmin } = useAuth();

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div className="navbar-left">
          <Link className="nav-link" to="/events">События</Link>
        </div>
        <nav className="navbar-right">
          {!user ? (
            <>
              <Link className="nav-link" to="/login">Вход</Link>
              <Link className="nav-link" to="/register">Регистрация</Link>
            </>
          ) : (
            <>
              <Link className="nav-link" to="/applications">Мои заявки</Link>
              <Link className="nav-link" to="/hours">Мои часы</Link>
              {isOrganizerOrAdmin && (
                <>
                  <Link className="nav-link" to="/events/create">Создать событие</Link>
                  <Link className="nav-link" to="/organizer/attendance">Посещаемость</Link>
                </>
              )}
              <button type="button" className="btn small danger" onClick={logout}>Выйти</button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
