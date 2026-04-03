import "../styles/settings.css";

function Settings() {
  return (
    <div className="settings-page">
      <div className="settings-header">

        <h1 className="settings-title">← Настройки</h1>

        <div className="header-right">
          <button className="icon-btn">🔔</button>

          <img
            src="https://i.pravatar.cc/40"
            alt="avatar"
            className="avatar"
          />
        </div>

      </div>
      <div className="settings-container">

        

        <div className="settings-list">

          <div className="settings-item">
            <div>
              <p className="settings-name">Личный кабинет</p>
            </div>
            <span className="arrow">›</span>
          </div>

          <div className="settings-item">
            <div>
              <p className="settings-name">Язык</p>
              <span className="settings-desc">Выбранный язык : Русский</span>
            </div>

            <select className="settings-select">
              <option>Русский</option>
              <option>English</option>
            </select>
          </div>

          <div className="settings-item">
            <div>
              <p className="settings-name">Горячие клавиши</p>
              <span className="settings-desc">
                View and customize keyboard shortcuts for quick actions.
              </span>
            </div>
            <span className="arrow">›</span>
          </div>

          <div className="settings-item">
            <div>
              <p className="settings-name">Тема</p>
            </div>

            <select className="settings-select">
              <option>Стандартная</option>
              <option>Тёмная</option>
              <option>Светлая</option>
            </select>
          </div>

          <div className="settings-item">
            <div>
              <p className="settings-name">Подписка</p>
            </div>
            <span className="arrow">›</span>
          </div>

          <div className="settings-item">
            <div>
              <p className="settings-name">Уведомления</p>
            </div>
            <span className="arrow">›</span>
          </div>

          <div className="settings-item logout">
            <p className="settings-name">Выйти</p>
          </div>

        </div>
      </div>

      <footer className="settings-footer">
        <p>© 2025 Melo.</p>
      </footer>
    </div>
  );
}

export default Settings;