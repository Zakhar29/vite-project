import "../styles/register.css";

function Register() {
  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-box">
          <button className="back-btn" onClick={() => window.history.back()}>
            ←
          </button>

          <h1>Регистрация</h1>
          <p className="register-subtitle">
            Получите доступ к нашим официальным ресурсам по брендингу, историям успеха и медиа-ресурсам. 
            Для начала заполните форму ниже.
          </p>

          <form className="register-form">
            <div className="form-group">
              <label>Full Name</label>
              <input type="text" placeholder="John Doe" required />
            </div>

            <div className="form-group">
              <label>Company Email</label>
              <input type="email" placeholder="john.doe@company.com" required />
            </div>

            <div className="form-group">
              <label>Purpose / Message</label>
              <textarea 
                placeholder="Briefly describe your request and how you plan to use the press kit." 
                rows="5"
                required
              />
            </div>

            <div className="checkbox-group">
              <input type="checkbox" id="agree" required />
              <label htmlFor="agree">
                Я согласен получать сообщения от нашей команды относительно пресс-подборки и связанных с ней обновлений.
              </label>
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