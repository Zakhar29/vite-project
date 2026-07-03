import { Link } from "react-router-dom";
import "../styles/threadFooter.css";

function ThreadFooter() {
  return (
    <footer className="thread-footer">
      <div className="thread-footer__inner">
        <div className="thread-footer__brand">
          <span className="thread-footer__logo-icon" aria-hidden="true">♪</span>
          <span className="thread-footer__logo-text">Melo</span>
        </div>

        <div className="thread-footer__social">
          <h4>Следите за нами</h4>
          <div className="thread-footer__icons">
            <a href="#" aria-label="Telegram">TG</a>
            <a href="#" aria-label="Instagram">IG</a>
            <a href="#" aria-label="YouTube">YT</a>
          </div>
        </div>

        <div className="thread-footer__newsletter">
          <h4>Следи за обновлениями</h4>
          <p>Получайте новости о релизах, обсуждениях и обновлениях платформы.</p>
          <form className="thread-footer__form" onSubmit={(e) => e.preventDefault()}>
            <input type="email" placeholder="Ваш email" />
            <button type="submit">Отправить</button>
          </form>
        </div>
      </div>

      <div className="thread-footer__copy">
        <Link to="/">© 2025 Melo.</Link>
      </div>
    </footer>
  );
}

export default ThreadFooter;
