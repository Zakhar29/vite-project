import { useState } from 'react';
import "../styles/navbar.css";
import { Link } from "react-router-dom";
import NotificationPopup from "./NotificationPopup";   // ← Убедись, что файл существует

function Navbar() {
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <header className="navbar">
      <div className="navbar__logo">Melo</div>

      <nav className="navbar__links">
        <Link to="/">Главная</Link>
        <Link to="/artists">Артисты</Link>
        <Link to="/discussions">Обсуждения</Link>
        <Link to="/soundpacks" className="active">Звуковые пакеты</Link>
      </nav>

      <div className="navbar__right">
        <input
          type="text"
          placeholder="Поиск музыки, артиста, альбома"
          className="navbar__search"
        />

        <div 
          className="notification-bell" 
          onClick={() => setShowNotifications(!showNotifications)}
        >
          🔔
        </div>

        <button className="login-btn">
          <Link to="/login">Войти</Link>
        </button>

        <button className="register-btn">
          <Link to="/register">Зарегистрироваться</Link>
        </button>
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