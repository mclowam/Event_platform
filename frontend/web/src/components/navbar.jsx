import React from "react";
import { Link } from "react-router-dom";

export default function Navbar({ currentUser, logout }) {
    return (
        <header className="navbar">
            <div className="navbar-inner">
                <div className="navbar-left">
                    <Link to="/" className="navbar-logo">
                        Events
                    </Link>
                </div>

                <nav className="navbar-right">
                    {!currentUser ? (
                        <>
                            <Link className="nav-link" to="/login">
                                Вход
                            </Link>
                            <Link className="nav-link" to="/register">
                                Регистрация
                            </Link>
                        </>
                    ) : (
                        <>
                            <Link className="nav-link" to="/profile">
                                Профиль
                            </Link>
                            <button className="btn small danger" onClick={logout}>
                                Выйти
                            </button>
                        </>
                    )}
                </nav>
            </div>
        </header>
    );
}
