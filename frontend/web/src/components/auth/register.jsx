import React, { useState } from "react";
import { apiRequest } from "../../services/apiService.js";

function Register() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [name, setName] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess("");
        setLoading(true);

        try {
            await apiRequest("auth/register/", {
                method: "POST",
                body: { email, password, name },
            });
            setSuccess("Регистрация прошла успешно. Теперь вы можете войти.");
            setEmail("");
            setPassword("");
            setName("");
        } catch (err) {
            setError(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <h2>Регистрация</h2>
            {error && (
                <div className="alert alert-error">
                    {typeof error === "string"
                        ? error
                        : error?.data
                        ? JSON.stringify(error.data)
                        : error.message || "Ошибка"}
                </div>
            )}
            {success && <div className="alert alert-success">{success}</div>}
            <form onSubmit={handleSubmit} className="form">
                <label className="field">
                    <span>Имя</span>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </label>
                <label className="field">
                    <span>Email</span>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </label>
                <label className="field">
                    <span>Пароль</span>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </label>
                <button className="btn primary" type="submit" disabled={loading}>
                    {loading ? "Загрузка..." : "Зарегистрироваться"}
                </button>
            </form>
        </div>
    );
}

export default Register;

