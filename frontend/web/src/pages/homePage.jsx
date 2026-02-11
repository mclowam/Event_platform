import React from "react";

function HomePage({ currentUser }) {
    return (
        <main className="page">
            <h1 className="page-title">Платформа событий</h1>
            <p className="page-subtitle">
                Здесь будут мероприятия, расписания и управление событиями.
            </p>

            {!currentUser ? (
                <p className="page-text">
                    Чтобы продолжить, войдите в аккаунт через кнопку «Вход» вверху.
                </p>
            ) : (
                <div className="card">
                    <h2>Добро пожаловать, {currentUser?.name || currentUser?.email || "пользователь"}!</h2>
                    <p className="page-text">
                        В ближайшее время здесь появится личный кабинет и ваши события.
                    </p>
                </div>
            )}
        </main>
    );
}

export default HomePage;

