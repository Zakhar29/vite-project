import "../styles/navbar.css";
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar__logo">Melo</div>

      <nav className="navbar__links">
        <a href="#">Главная</a>
        <a href="#">Артисты</a>
        <a href="#">Обсуждения</a>
        <a href="#" className="active">Звуковые пакеты</a>
      </nav>

      <div className="navbar__right">
        <input
          type="text"
          placeholder="Поиск музыки, артиста, альбома"
          className="navbar__search"
        />
        <Link to="/notifications">
          🔔
        </Link>
        <button className="login-btn"><Link to= "/login">Войти</Link></button>
        <button className="register-btn">Зарегистрироваться</button>
      </div>
    </header>
  );
}

export default Navbar;