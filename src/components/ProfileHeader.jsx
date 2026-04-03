function ProfileHeader() {
  return (
    <div className="profile-header">

      <div className="profile-left">

        <img
          src="https://i.pravatar.cc/100"
          className="profile-avatar"
        />

        <div>
          <h1>ZAKHAR</h1>

          <p>
            Преданный своему делу продюсер и диджей
            создает яркие звуковые ландшафты
            в стиле синтвейв.
          </p>
        </div>

      </div>

      <div className="profile-right">

        <div className="profile-stats">
          <div>
            <span className="count blue">123</span>
            <p>Подписчиков</p>
          </div>

          <div>
            <span className="count purple">120</span>
            <p>Подписок</p>
          </div>
        </div>

        <button className="follow-btn">
          Подписаться
        </button>

      </div>

    </div>
  );
}

export default ProfileHeader;