import "../styles/premium.css";

function Premium() {
  return (
    <div className="premium-page">
      <div className="premium-page__inner">
      <div className="premium-header">
        <button className="back-btn" onClick={() => window.history.back()}>
          ← Подписка
        </button>
      </div>

      {/* Главное предложение */}
      <div className="premium-offer">
        <div className="offer-text">
          <h1>Откройте для себя мир безграничных возможностей</h1>
          <p>
            с нашей эксклюзивной подпиской! Получите доступ к уникальным 
            функциям, которые помогут вам раскрыть весь потенциал вашего 
            музыкального творчества и общения.
          </p>
        </div>

        <div className="offer-visual">
          <img 
            src="https://picsum.photos/id/1015/620/520" 
            alt="Melo Premium" 
          />
        </div>
      </div>

      {/* Что входит в подписку */}
      <div className="benefits-section">
        <h2>Что входит в подписку</h2>
        
        <div className="benefits-list">
          <div className="benefit">
            <h3>Эксклюзивный контент</h3>
            <p>Используйте подписку на сайте — для покупки уникального контента, бонусов и поощрений.</p>
          </div>
          
          <div className="benefit">
            <h3>Закрытые сообщества</h3>
            <p>Делитесь музыкой и общайтесь в приватных группах с друзьями или подписчиками.</p>
          </div>
          
          <div className="benefit">
            <h3>Продвижение</h3>
            <p>Поднимайте ваши треки и проекты в рекомендациях и топах, чтобы вас услышали все.</p>
          </div>
        </div>
      </div>

      {/* Цена и кнопка */}
      <div className="pricing-box">
        <h2>Стоимость: <span className="price">249 рублей</span> / месяц</h2>
        <button 
          className="pay-button"
          onClick={() => window.location.href = '/subscription'}
        >
          Оплатить
        </button>
      </div>
      </div>
    </div>
  );
}

export default Premium;