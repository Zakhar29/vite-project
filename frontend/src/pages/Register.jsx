import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/register.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    nickname: "", // добавляем nickname
    bio: "",
    agree: false,
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState("");

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
    // Очищаем ошибку при вводе
    if (errors[name]) {
      setErrors({ ...errors, [name]: "" });
    }
    if (serverError) setServerError("");
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = "Введите имя пользователя";
    } else if (formData.username.length < 3) {
      newErrors.username = "Имя пользователя должно быть не менее 3 символов";
    } else if (formData.username.length > 30) {
      newErrors.username = "Имя пользователя должно быть не более 30 символов";
    }

    if (!formData.nickname.trim()) {
      newErrors.nickname = "Введите никнейм";
    } else if (formData.nickname.length < 2) {
      newErrors.nickname = "Никнейм должен быть не менее 2 символов";
    } else if (formData.nickname.length > 30) {
      newErrors.nickname = "Никнейм должен быть не более 30 символов";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Введите email";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Некорректный email";
    }

    if (!formData.password) {
      newErrors.password = "Введите пароль";
    } else if (formData.password.length < 6) {
      newErrors.password = "Пароль должен быть не менее 6 символов";
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Пароли не совпадают";
    }

    if (!formData.agree) {
      newErrors.agree = "Необходимо подтвердить согласие";
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
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: formData.username.trim(),
          email: formData.email.trim(),
          password: formData.password,
          nickname: formData.nickname.trim(),
        }),
        credentials: "include",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Ошибка регистрации");
      }

      // Сохраняем токен
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
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
    <div className="register-page">
      <div className="register-container">
        <div className="register-box">
          <button className="back-btn" onClick={() => window.history.back()}>
            ←
          </button>

          <h1>Регистрация</h1>
          <p className="register-subtitle">
            Присоединяйтесь к сообществу независимых музыкантов. Делитесь треками, получайте обратную связь и развивайте творчество.
          </p>

          {serverError && (
            <div className="server-error">
              {serverError}
            </div>
          )}

          <form className="register-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Имя пользователя (username) *</label>
              <input
                type="text"
                name="username"
                placeholder="Например: electro_cat"
                value={formData.username}
                onChange={handleChange}
                disabled={isLoading}
                required
              />
              {errors.username && <span className="error-text">{errors.username}</span>}
              <small className="hint">Только латиница, цифры и знак подчёркивания. 3–30 символов.</small>
            </div>

            <div className="form-group">
              <label>Никнейм (отображаемое имя) *</label>
              <input
                type="text"
                name="nickname"
                placeholder="Например: Electro Cat"
                value={formData.nickname}
                onChange={handleChange}
                disabled={isLoading}
                required
              />
              {errors.nickname && <span className="error-text">{errors.nickname}</span>}
              <small className="hint">Имя, которое увидят другие пользователи. 2–30 символов.</small>
            </div>

            <div className="form-group">
              <label>Email *</label>
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
              <label>Пароль *</label>
              <input
                type="password"
                name="password"
                placeholder="Не менее 6 символов"
                value={formData.password}
                onChange={handleChange}
                disabled={isLoading}
                required
              />
              {errors.password && <span className="error-text">{errors.password}</span>}
            </div>

            <div className="form-group">
              <label>Подтверждение пароля *</label>
              <input
                type="password"
                name="confirmPassword"
                placeholder="Повторите пароль"
                value={formData.confirmPassword}
                onChange={handleChange}
                disabled={isLoading}
                required
              />
              {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
            </div>

            <div className="form-group">
              <label>О себе (необязательно)</label>
              <textarea
                name="bio"
                placeholder="Расскажите о своём музыкальном стиле, инструментах или проектах..."
                rows="4"
                value={formData.bio}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>

            <div className="checkbox-group">
              <input
                type="checkbox"
                name="agree"
                id="agree"
                checked={formData.agree}
                onChange={handleChange}
                disabled={isLoading}
                required
              />
              <label htmlFor="agree">
                Я принимаю условия пользовательского соглашения и даю согласие на обработку персональных данных.
              </label>
              {errors.agree && <span className="error-text">{errors.agree}</span>}
            </div>

            <button
              type="submit"
              className="register-submit-btn"
              disabled={isLoading}
            >
              {isLoading ? "Регистрация..." : "Зарегистрироваться"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Register;