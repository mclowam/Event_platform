import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';
import { ROLES } from '../config/index.js';

/**
 * Require auth. If roleRequired is set (e.g. 'organizer'), user.role must be organizer or admin.
 */
export default function ProtectedRoute({ children, roleRequired }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <main className="page">
        <p className="page-text">Загрузка...</p>
      </main>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (roleRequired === ROLES.organizer) {
    const allowed = user.role === ROLES.organizer || user.role === ROLES.admin;
    if (!allowed) {
      return <Navigate to="/events" replace />;
    }
  }

  return children;
}
