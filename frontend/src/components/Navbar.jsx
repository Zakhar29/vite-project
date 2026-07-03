import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation, NavLink } from "react-router-dom";
import "../styles/navbar.css";
import NotificationPopup from "./NotificationPopup";
import AvatarMenu from "./AvatarMenu";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showAvatarMenu, setShowAvatarMenu] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const token = localStorage.getItem("access_token");
  const isThreadPage = location.pathname.startsWith("/discussion/");
  const isDiscussionsPage = location.pathname === "/discussions";

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
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
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

  const handleSearch = (e) => {
    if (e.key === "Enter") {
      const query = e.target.value.trim();
      if (query) {
        navigate(`/search?q=${encodeURIComponent(query)}`);
      }
    }
  };

  return (
    <header className={`navbar ${isThreadPage ? "navbar--thread" : ""}`}>
      <div className="navbar__left">
        {isThreadPage && (
          <button
            type="button"
            className="navbar__back"
            onClick={() => navigate(-1)}
            aria-label="Назад"
          >
            ←
          </button>
        )}

        <div className="navbar__logo" onClick={() => navigate("/")}>
          <span className="navbar__logo-icon" aria-hidden="true">♪</span>
          <span>Melo</span>
        </div>
      </div>

      <nav className="navbar__links">
        <NavLink to="/" end>Главная</NavLink>
        <NavLink to="/search">Артисты</NavLink>
        <NavLink to="/discussions">Обсуждения</NavLink>
        <NavLink to="/soundpacks">Звуковые панели</NavLink>
      </nav>

      <div className="navbar__right">
        {isDiscussionsPage && (
          <button
            type="button"
            className="navbar__create-discussion"
            onClick={() => window.dispatchEvent(new Event("openCreateDiscussion"))}
          >
            + Создать обсуждение
          </button>
        )}

        {!isThreadPage && (
          <div className="navbar__search-wrap">
            <span className="navbar__search-icon" aria-hidden="true">⌕</span>
            <input
              type="text"
              placeholder={isDiscussionsPage ? "дискуссии, артисты или жанр" : "дискуссии, артисты или жанры"}
              className="navbar__search"
              onKeyDown={handleSearch}
            />
          </div>
        )}

        {!isDiscussionsPage && (
          <Link to="/create-release" className="navbar__icon-btn" title="Загрузить">
            ↑
          </Link>
        )}

        <button
          type="button"
          className="navbar__icon-btn navbar__bell"
          onClick={() => setShowNotifications(!showNotifications)}
          aria-label="Уведомления"
        >
          🔔
        </button>

        {isLoading ? (
          <div className="navbar__loading">...</div>
        ) : user ? (
          <AvatarMenu
            user={user}
            isOpen={showAvatarMenu}
            onToggle={() => setShowAvatarMenu((prev) => !prev)}
            onClose={() => setShowAvatarMenu(false)}
          />
        ) : (
          <div className="navbar__auth-buttons">
            <Link to="/login" className="login-btn">Войти</Link>
            <Link to="/register" className="register-btn">Регистрация</Link>
          </div>
        )}
      </div>

      <NotificationPopup
        isOpen={showNotifications}
        onClose={() => setShowNotifications(false)}
      />
    </header>
  );
}

export default Navbar;
