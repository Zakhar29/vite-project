import "../styles/login.css";

function Login() {
  return (
    <div className="login-page">

      {/* стрелка назад */}
      <div className="back-btn">←</div>

      <div className="login-card">

        <h1>Вход</h1>

        <div className="form-group">
          <label>Full Name</label>
          <input placeholder="John Doe" />
        </div>

        <div className="form-group">
          <label>Company Email</label>
          <input placeholder="john.doe@company.com" />
        </div>

        <button className="login-btn">
          Войти
        </button>

      </div>
    </div>
  );
}

export default Login;