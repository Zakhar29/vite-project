import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles/settings.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Settings() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [settings, setSettings] = useState({
    language: "Русский",
    theme: "Стандартная",
  });
  const [isLoading, setIsLoading] = useState(true);

  const token = localStorage.getItem("access_token");

  // ========== Получение данных пользователя ==========

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    fetchUserData();
  }, []);

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
        localStorage.removeItem("access_token");
        navigate("/login");
      }
    } catch (error) {
      console.error("Ошибка загрузки пользователя:", error);
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
      navigate("/login");
    }
  };

  // ========== Обновление настроек ==========

  const handleSettingChange = async (key, value) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    // TODO: Отправить изменения на сервер
  };

  // ========== Навигация ==========

  const goToProfileEdit = () => {
    navigate("/profile/edit");
  };

  const goToSubscription = () => {
    navigate("/subscription");
  };

  const goToNotifications = () => {
    navigate("/notifications");
  };

  // ========== Состояние загрузки ==========

  if (isLoading) {
    return (
      <div className="settings-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Загрузка настроек...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="settings-page">
        <div className="error-container">
          <p>Пожалуйста, войдите в систему</p>
          <Link to="/login" className="login-link">Войти</Link>
        </div>
      </div>
    );
  }

  // ========== Рендер ==========

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1 className="settings-title" onClick={() => navigate(-1)}>
          ← Настройки
        </h1>
      </div>

      <div className="settings-container">

        {/* Профиль пользователя */}
        <div className="settings-profile">
          <img
            src={user.avatar_url || "/default-avatar.png"}
            alt={user.nickname}
            className="settings-avatar"
          />
          <div className="settings-profile-info">
            <p className="settings-profile-name">{user.nickname}</p>
            <p className="settings-profile-email">{user.email || "email@example.com"}</p>
          </div>
        </div>

        <div className="settings-list">

          {/* Личный кабинет — переход на /profile/edit */}
          <div className="settings-item clickable" onClick={goToProfileEdit}>
            <div>
              <p className="settings-name">Личный кабинет</p>
              <span className="settings-desc">Редактировать профиль и настройки аккаунта</span>
            </div>
            <span className="arrow">›</span>
          </div>

          {/* Язык */}
          <div className="settings-item">
            <div>
              <p className="settings-name">Язык</p>
              <span className="settings-desc">Выбранный язык: {settings.language}</span>
            </div>
            <select
              className="settings-select"
              value={settings.language}
              onChange={(e) => handleSettingChange("language", e.target.value)}
            >
              <option value="Русский">Русский</option>
              <option value="English">English</option>
              <option value="Қазақша">Қазақша</option>
            </select>
          </div>

          {/* Горячие клавиши */}
          <div className="settings-item clickable">
            <div>
              <p className="settings-name">Горячие клавиши</p>
              <span className="settings-desc">
                Просмотр и настройка сочетаний клавиш для быстрых действий
              </span>
            </div>
            <span className="arrow">›</span>
          </div>

          {/* Тема */}
          <div className="settings-item">
            <div>
              <p className="settings-name">Тема</p>
              <span className="settings-desc">Цветовая схема интерфейса</span>
            </div>
            <select
              className="settings-select"
              value={settings.theme}
              onChange={(e) => handleSettingChange("theme", e.target.value)}
            >
              <option value="Стандартная">Стандартная</option>
              <option value="Тёмная">Тёмная</option>
              <option value="Светлая">Светлая</option>
            </select>
          </div>

          {/* Подписка — переход на /subscription */}
          <div className="settings-item clickable" onClick={goToSubscription}>
            <div>
              <p className="settings-name">Подписка</p>
              <span className="settings-desc">Управление платным тарифом</span>
            </div>
            <span className="arrow">›</span>
          </div>

          {/* Уведомления — переход на /notifications */}
          <div className="settings-item clickable" onClick={goToNotifications}>
            <div>
              <p className="settings-name">Уведомления</p>
              <span className="settings-desc">Настройка оповещений</span>
            </div>
            <span className="arrow">›</span>
          </div>

          {/* Выход */}
          <div className="settings-item logout" onClick={handleLogout}>
            <p className="settings-name">Выйти</p>
          </div>

        </div>
      </div>

      <footer className="settings-footer">
        <p>© 2025 Melo. Все права защищены.</p>
        <p className="settings-version">Версия 1.0.0</p>
      </footer>
    </div>
  );
}

export default Settings;