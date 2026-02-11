import { apiRequest, setTokens } from "../../services/apiService.js";
import { useState } from "react";

function Login({ onLogin }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [success, setSuccess] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess("");
        setLoading(true);

        try {
            const tokensResponse = await apiRequest("auth/login/", {
                method: "POST",
                body: { email, password },
            });

            const normalizedTokens =
                tokensResponse && (tokensResponse.access || tokensResponse.refresh)
                    ? tokensResponse
                    : {
                          access: tokensResponse.access_token,
                          refresh: tokensResponse.refresh_token,
                      };

            setTokens(normalizedTokens);

            const me = await apiRequest("auth/me/");
            if (onLogin) {
                onLogin(me);
            }

            setSuccess("Успешный вход");
        } catch (err) {
            setError(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <h2>вход</h2>
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
                    <span>Email</span>
                    <input
                        type="text"
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
                    {loading ? "Загрузка..." : "Войти"}
                </button>
            </form>
        </div>
    );
}

export default Login;
