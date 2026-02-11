import Navbar from "./components/navbar.jsx";
import { useEffect, useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { apiRequest, loadTokensFromStorage, setTokens } from "./services/apiService.js";
import Login from "./components/auth/login.jsx";
import Register from "./components/auth/register.jsx";
import HomePage from "./pages/homePage.jsx";
import './App.css'

function App() {
    const [currentUser, setCurrentUser] = useState(null);

    useEffect(() => {
        const tokens = loadTokensFromStorage();
        if (tokens) {
            apiRequest("auth/me/")
                .then((user) => setCurrentUser(user))
                .catch(() => {
                    setTokens(null);
                    setCurrentUser(null);
                });
        }
    }, []);

    const logout = () => {
        setTokens(null);
        setCurrentUser(null);
    };

    return (
        <>
            <Navbar currentUser={currentUser} logout={logout} />

            <Routes>
                <Route
                    path="/"
                    element={<HomePage currentUser={currentUser} />}
                />

                <Route
                    path="/login"
                    element={
                        !currentUser ? (
                            <Login onLogin={setCurrentUser} />
                        ) : (
                            <Navigate to="/" />
                        )
                    }
                />

                <Route
                    path="/register"
                    element={
                        !currentUser ? (
                            <Register />
                        ) : (
                            <Navigate to="/" />
                        )
                    }
                />
            </Routes>
        </>
    );
}

export default App;
