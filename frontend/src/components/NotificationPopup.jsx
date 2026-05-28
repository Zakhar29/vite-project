import { Link } from "react-router-dom";
import "../styles/notificationPopup.css";

function NotificationPopup({ isOpen, onClose }) {

  const notifications = [
    {
      id: 1,
      text: "Новый комментарий под твоим треком",
      time: "2 минуты назад"
    },
    {
      id: 2,
      text: "Новый комментарий под твоим треком",
      time: "5 минут назад"
    },
    {
      id: 3,
      text: "Ваш трек добавили в плейлист",
      time: "23 минуты назад"
    },
  ];

  if (!isOpen) return null;

  return (
    <div className="notification-popup-overlay" onClick={onClose}>
      <div className="notification-popup" onClick={e => e.stopPropagation()}>
        <div className="popup-header">
          <h3>Уведомления</h3>
          <button className="close-popup" onClick={onClose}>✕</button>
        </div>

        <div className="popup-notifications">
          {notifications.map(n => (
            <div className="popup-notification" key={n.id}>
              <div className="popup-icon">💬</div>
              <div className="popup-content">
                <p>{n.text}</p>
                <span>{n.time}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="popup-footer">
          <Link to="/notifications" onClick={onClose}>
            <button className="view-all-btn">
              Все уведомления
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default NotificationPopup;