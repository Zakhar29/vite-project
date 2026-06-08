import { useState } from "react";
import "../styles/register.css";

function Register() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    bio: "",
    agree: false,
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.username.trim()) newErrors.username = "Введите имя пользователя";
    if (!formData.email.trim()) newErrors.email = "Введите email";
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = "Некорректный email";
    if (!formData.password) newErrors.password = "Введите пароль";
    else if (formData.password.length < 6) newErrors.password = "Пароль должен быть не менее 6 символов";
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = "Пароли не совпадают";
    if (!formData.agree) newErrors.agree = "Необходимо подтвердить согласие";
    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
    } else {
      // Отправка данных на сервер (заглушка)
      console.log("Отправка данных:", formData);
      alert("Регистрация успешна! (демо)");
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

          <form className="register-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Имя пользователя (никнейм)</label>
              <input
                type="text"
                name="username"
                placeholder="Например: ElectroCat"
                value={formData.username}
                onChange={handleChange}
                required
              />
              {errors.username && <span className="error-text">{errors.username}</span>}
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                placeholder="your@email.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            <div className="form-group">
              <label>Пароль</label>
              <input
                type="password"
                name="password"
                placeholder="Не менее 6 символов"
                value={formData.password}
                onChange={handleChange}
                required
              />
              {errors.password && <span className="error-text">{errors.password}</span>}
            </div>

            <div className="form-group">
              <label>Подтверждение пароля</label>
              <input
                type="password"
                name="confirmPassword"
                placeholder="Повторите пароль"
                value={formData.confirmPassword}
                onChange={handleChange}
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
              />
            </div>

            <div className="checkbox-group">
              <input
                type="checkbox"
                name="agree"
                id="agree"
                checked={formData.agree}
                onChange={handleChange}
                required
              />
              <label htmlFor="agree">
                Я принимаю условия пользовательского соглашения и даю согласие на обработку персональных данных.
              </label>
              {errors.agree && <span className="error-text">{errors.agree}</span>}
            </div>

            <button type="submit" className="register-submit-btn">
              Зарегистрироваться
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Register;