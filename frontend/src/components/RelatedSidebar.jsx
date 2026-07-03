function RelatedSidebar() {
  return (
    <aside className="thread-sidebar">
      <div className="sidebar-card">
        <h3>Связанные с этим обсуждения</h3>
        <ul>
          <li>Лучшие альбомы для дождливого дня?</li>
          <li>Артисты, расширяющие границы</li>
          <li>Скрытые жемчужины инди-лейблов</li>
          <li>Эволюция потоковой музыки</li>
        </ul>
      </div>

      <div className="sidebar-card">
        <h3>Правила коммьюнити</h3>
        <ul>
          <li>Будьте уважительны</li>
          <li>Без оскорблений и хейта</li>
          <li>Обсуждайте музыку</li>
          <li>Сообщайте о нарушениях</li>
        </ul>
      </div>
    </aside>
  );
}

export default RelatedSidebar;
