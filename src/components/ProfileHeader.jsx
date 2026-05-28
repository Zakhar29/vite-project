import { useState, useEffect } from 'react';

function ProfileHeader() {
  const [profileData, setProfileData] = useState({
    avatar: '',
    name: '',
    bio: ''
  });

  useEffect(() => {
    // Загружаем данные из localStorage при монтировании
    const avatar = localStorage.getItem('profileAvatar') || 'https://i.pravatar.cc/100';
    const name = localStorage.getItem('profileName') || 'ZAKHAR';
    const bio = localStorage.getItem('profileBio') || 'Преданный своему делу продюсер и диджей создает яркие звуковые ландшафты в стиле синтвейв. Преданный своему делу продюсер и диджей создает яркие звуковые ландшафты в стиле синтвейв. Преданный своему делу продюсер и диджей создает яркие звуковые ландшафты в стиле синтвейв. Преданный своему делу продюсер и диджей создает яркие звуковые ландшафты в стиле синтвейв.';
    setProfileData({ avatar, name, bio });
  }, []);
  return (
    <div className="profile-header">

      <div className="profile-left">

        <img
          src="https://i.pravatar.cc/100"
          className="profile-avatar"
        />

        <div>
          <h1>ZAKHAR</h1>

            <div className="text_prof"><p>
              Преданный своему делу продюсер и диджей
              создает яркие звуковые ландшафты
              в стиле синтвейв.
              Преданный своему делу продюсер и диджей
              создает яркие звуковые ландшафты
              в стиле синтвейв.
              Преданный своему делу продюсер и диджей
              создает яркие звуковые ландшафты
              в стиле синтвейв.
              Преданный своему делу продюсер и диджей
              создает яркие звуковые ландшафты
              в стиле синтвейв.
            </p></div>
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

        

      </div>

    </div>
  );
}

export default ProfileHeader;