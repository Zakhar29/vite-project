import { useState, useEffect } from 'react';
import { Link, useNavigate } from "react-router-dom";
import "../styles/navbar.css";
import NotificationPopup from "./NotificationPopup";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Navbar() {
  const navigate = useNavigate();
  const [showNotifications, setShowNotifications] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const token = localStorage.getItem("access_token");

  // ========== Получение данных пользователя ==========

  useEffect(() => {
    if (token) {
      fetchUserData();
    } else {
      setIsLoading(false);
      setUser(null);
    }
  }, [token]);

  const fetchUserData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        // Токен невалидный — удаляем
        localStorage.removeItem("access_token");
        setUser(null);
      }
    } catch (error) {
      console.error("Ошибка загрузки пользователя:", error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  // ========== Выход ==========

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/api/v1/auth/logout`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        credentials: "include",
      });
    } catch (error) {
      console.error("Ошибка выхода:", error);
    } finally {
      localStorage.removeItem("access_token");
      setUser(null);
      navigate("/login");
    }
  };

  // ========== Поиск ==========

  const handleSearch = (e) => {
    if (e.key === "Enter") {
      const query = e.target.value.trim();
      if (query) {
        navigate(`/search?q=${encodeURIComponent(query)}`);
      }
    }
  };

  // ========== Рендер ==========

  return (
    <header className="navbar">
      <div className="navbar__logo" onClick={() => navigate("/")}>
        Melo
      </div>

      <nav className="navbar__links">
        <Link to="/">Главная</Link>
        <Link to="/feed">Лента</Link>
        <Link to="/discussions">Обсуждения</Link>
        <Link to="/soundpacks">Звуковые пакеты</Link>
      </nav>

      <div className="navbar__right">
        <input
          type="text"
          placeholder="Поиск музыки, артиста, альбома"
          className="navbar__search"
          onKeyDown={handleSearch}
        />

        <div
          className="notification-bell"
          onClick={() => setShowNotifications(!showNotifications)}
        >
          🔔
        </div>

        {/* ===== БЛОК АВТОРИЗАЦИИ ===== */}

        {isLoading ? (
          // Загрузка
          <div className="navbar__loading">...</div>

        ) : user ? (
          // Авторизован — показываем аватар + имя
          <div className="navbar__user">
            <img
              src={user.avatar_url || "/default-avatar.png"}
              className="navbar__avatar"
              onClick={() => navigate(`/profile/me`)}
            />
            <span className="navbar__username" onClick={() => navigate(`/profile/${user.id}`)}>
              {user.nickname}
            </span>
            <button className="navbar__logout" onClick={handleLogout}>
              Выйти
            </button>
          </div>

        ) : (
          // Не авторизован — кнопки входа/регистрации
          <div className="navbar__auth-buttons">
            <Link to="/login" className="login-btn">
              Войти
            </Link>
            <Link to="/register" className="register-btn">
              Зарегистрироваться
            </Link>
          </div>
        )}
      </div>

      {/* Попап с уведомлениями */}
      <NotificationPopup
        isOpen={showNotifications}
        onClose={() => setShowNotifications(false)}
      />
    </header>
  );
}

export default Navbar;