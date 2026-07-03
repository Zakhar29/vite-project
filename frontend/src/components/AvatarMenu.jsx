import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import Avatar from "./Avatar";
import "../styles/avatarMenu.css";

function ProfileIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path d="M5 20c0-3.3 3.1-6 7-6s7 2.7 7 6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function SubscriptionIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <path d="M7 8h10l-1.2 10H8.2L7 8z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M9 8V6a3 3 0 0 1 6 0v2" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function SettingsIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 3v2m0 14v2M3 12h2m14 0h2M5.6 5.6l1.4 1.4m10 10 1.4 1.4m0-12.8-1.4 1.4m-10 10-1.4 1.4"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

const MENU_ITEMS = [
  { key: "profile", label: "Профиль", to: (user) => `/profile/${user.id}`, icon: ProfileIcon },
  { key: "subscription", label: "Подписка", to: () => "/subscription", icon: SubscriptionIcon },
  { key: "settings", label: "Настройки", to: () => "/settings", icon: SettingsIcon },
];

function AvatarMenu({ user, isOpen, onToggle, onClose }) {
  const menuRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return undefined;

    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        onClose();
      }
    };

    const handleEscape = (event) => {
      if (event.key === "Escape") onClose();
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen, onClose]);

  if (!user) return null;

  return (
    <div className="avatar-menu" ref={menuRef}>
      <button
        type="button"
        className={`avatar-menu__trigger ${isOpen ? "is-open" : ""}`}
        onClick={onToggle}
        aria-label="Меню профиля"
        aria-expanded={isOpen}
        aria-haspopup="menu"
      >
        <Avatar
          src={user.avatar_url}
          className="avatar-menu__avatar"
          alt={user.nickname}
        />
      </button>

      {isOpen && (
        <div className="avatar-menu__dropdown" role="menu">
          {MENU_ITEMS.map(({ key, label, to, icon: Icon }) => (
            <Link
              key={key}
              to={typeof to === "function" ? to(user) : to}
              className="avatar-menu__item"
              role="menuitem"
              onClick={onClose}
            >
              <span className="avatar-menu__icon">
                <Icon />
              </span>
              <span>{label}</span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default AvatarMenu;
