import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles/login.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    // Очищаем ошибку при вводе
    if (errors[name]) {
      setErrors({ ...errors, [name]: "" });
    }
    if (serverError) setServerError("");
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.email.trim()) {
      newErrors.email = "Введите email";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Некорректный email";
    }

    if (!formData.password) {
      newErrors.password = "Введите пароль";
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);
    setServerError("");

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formData.email.trim(),
          password: formData.password,
        }),
        credentials: "include",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Ошибка входа");
      }

      // Сохраняем access_token
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
      }
      if (data.refresh_token) {
        localStorage.setItem("refresh_token", data.refresh_token);
      }

      // Перенаправляем на главную
      navigate("/");

    } catch (error) {
      setServerError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">

      <div className="back-btn" onClick={() => window.history.back()}>
        ←
      </div>

      <div className="login-card">

        <h1>Вход</h1>

        {serverError && (
          <div className="server-error">
            {serverError}
          </div>
        )}

        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              placeholder="your@email.com"
              value={formData.email}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
            {errors.email && <span className="error-text">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label>Пароль</label>
            <input
              type="password"
              name="password"
              placeholder="••••••"
              value={formData.password}
              onChange={handleChange}
              disabled={isLoading}
              required
            />
            {errors.password && <span className="error-text">{errors.password}</span>}
          </div>

          <button
            type="submit"
            className="login-btn"
            disabled={isLoading}
          >
            {isLoading ? "Вход..." : "Войти"}
          </button>

        </form>

        <div className="login-footer">
          <p>
            Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
          </p>
          <Link to="/forgot-password" className="forgot-link">
            Забыли пароль?
          </Link>
        </div>

      </div>
    </div>
  );
}

export default Login;