import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.jsx';
import Layout from './components/Layout.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import Login from './components/auth/Login.jsx';
import Register from './components/auth/Register.jsx';
import EventsPage from './pages/EventsPage.jsx';
import EventDetailPage from './pages/EventDetailPage.jsx';
import MyApplicationsPage from './pages/MyApplicationsPage.jsx';
import CreateEventPage from './pages/CreateEventPage.jsx';
import OrganizerAttendancePage from './pages/OrganizerAttendancePage.jsx';
import VolunteerHoursPage from './pages/VolunteerHoursPage.jsx';
import { ROLES } from './config/index.js';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Navigate to="/events" replace />} />
          <Route path="events" element={<EventsPage />} />
          <Route path="events/:id" element={<EventDetailPage />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
          <Route path="applications" element={<ProtectedRoute><MyApplicationsPage /></ProtectedRoute>} />
          <Route path="hours" element={<ProtectedRoute><VolunteerHoursPage /></ProtectedRoute>} />
          <Route path="events/create" element={<ProtectedRoute roleRequired={ROLES.organizer}><CreateEventPage /></ProtectedRoute>} />
          <Route path="organizer/attendance" element={<ProtectedRoute roleRequired={ROLES.organizer}><OrganizerAttendancePage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/events" replace />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}

export default App;
