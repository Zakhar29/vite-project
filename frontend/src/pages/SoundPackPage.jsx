import "../styles/soundpack.css";

const MOCK_PACK = {
  id: "1",
  title: "Глубокие басовые в стиле Хаус",
  author: "CyberSynth Audio",
  coverUrl: "https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=600&h=600&fit=crop",
  description:
    "Окунитесь в атмосферу будущего с этим эксклюзивным пакетом звуков. Идеально подходит для создания саундтреков к киберпанк-играм, футуристическим видео и электронной музыке. Включает в себя мощные басовые линии, атмосферные падды и ударные элементы.",
  tags: ["Киберпанк", "Электроника", "Синтезаторы", "Драм-машина", "Эмбиент"],
  downloads: "12,589",
  size: "750 МБ",
};

const MOCK_TRACKS = [
  { id: "1", name: "Neon Streets Ambient", duration: "0:45", bpm: "120 BPM", key: "Cm", genre: "Эмбиент" },
  { id: "2", name: "Cybernetic Pulse", duration: "1:12", bpm: "128 BPM", key: "Am", genre: "Синт" },
  { id: "3", name: "Deep House Groove", duration: "0:58", bpm: "124 BPM", key: "Fm", genre: "Бас" },
  { id: "4", name: "Retro Future Lead", duration: "1:05", bpm: "110 BPM", key: "Gm", genre: "Лид" },
  { id: "5", name: "Industrial Kick", duration: "0:32", bpm: "130 BPM", key: "—", genre: "Ударные" },
  { id: "6", name: "Synthwave Arp", duration: "0:50", bpm: "118 BPM", key: "Dm", genre: "Арп" },
];

const MOCK_RECOMMENDATIONS = [
  {
    id: "r1",
    title: "Космическая Одиссея",
    author: "StarDust Beats",
    coverUrl: "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=160&h=160&fit=crop",
  },
  {
    id: "r2",
    title: "Ретро Вейв Сборник",
    author: "80s Rewind",
    coverUrl: "https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=160&h=160&fit=crop",
  },
  {
    id: "r3",
    title: "Лоу-фай Хип-Хоп Биты",
    author: "ChillGrooves",
    coverUrl: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=160&h=160&fit=crop",
  },
];

const MOCK_REVIEWS = [
  {
    id: "rev1",
    author: "SynthExplorer",
    rating: 5,
    text: "Этот пак просто бомба! Отлично подходит для нового трека в стиле киберпанк. Качество сэмплов на высоте, бас ложится идеально.",
  },
  {
    id: "rev2",
    author: "BeatMaker_99",
    rating: 5,
    text: "Использовал для саундтрека к игре — получилось атмосферно и мощно. Рекомендую всем, кто делает электронику.",
  },
];

function PackHeader({ pack }) {
  return (
    <section className="pack-hero">
      <div className="pack-hero__cover">
        <img src={pack.coverUrl} alt={pack.title} loading="lazy" />
      </div>

      <div className="pack-hero__info">
        <h1 className="pack-hero__title">{pack.title}</h1>
        <p className="pack-hero__author">{pack.author}</p>
        <p className="pack-hero__description">{pack.description}</p>

        <div className="pack-hero__tags">
          {pack.tags.map((tag) => (
            <span key={tag} className="pack-hero__tag">
              {tag}
            </span>
          ))}
        </div>

        <div className="pack-hero__stats">
          <span>⬇ {pack.downloads} загрузок</span>
          <span>💾 {pack.size}</span>
        </div>

        <button type="button" className="pack-hero__download">
          Скачать пакет
        </button>
      </div>
    </section>
  );
}

function PackTrack({ track }) {
  return (
    <div className="pack-track-row">
      <span className="pack-track-row__name">{track.name}</span>

      <div className="pack-track-row__meta">
        <span>{track.duration}</span>
        <span>{track.bpm}</span>
        <span>{track.key}</span>
        <span className="pack-track-row__genre">{track.genre}</span>
      </div>

      <div className="pack-track-row__actions">
        <button type="button" className="pack-track-row__play" aria-label="Воспроизвести">
          ▶
        </button>
        <button type="button" className="pack-track-row__download">
          <span aria-hidden="true">⬇</span>
          Скачать
        </button>
      </div>
    </div>
  );
}

function PackSidebar({ items }) {
  return (
    <aside className="pack-sidebar-block">
      <h3 className="pack-sidebar-block__title">Вам также может понравиться</h3>

      <div className="pack-recommend-list">
        {items.map((item) => (
          <button key={item.id} type="button" className="pack-recommend-card">
            <img src={item.coverUrl} alt="" loading="lazy" />
            <div>
              <p className="pack-recommend-card__title">{item.title}</p>
              <span className="pack-recommend-card__author">{item.author}</span>
            </div>
          </button>
        ))}
      </div>
    </aside>
  );
}

function PackReview({ review }) {
  return (
    <article className="pack-review-card">
      <div className="pack-review-card__header">
        <div className="pack-review-card__avatar" aria-hidden="true">
          {review.author.charAt(0)}
        </div>
        <div>
          <b className="pack-review-card__author">{review.author}</b>
          <span className="pack-review-card__stars" aria-label={`${review.rating} из 5`}>
            {"★".repeat(review.rating)}
          </span>
        </div>
      </div>
      <p className="pack-review-card__text">{review.text}</p>
    </article>
  );
}

function SoundPackPage() {
  return (
    <div className="soundpack-page">
      <div className="soundpack-page__inner">
        <div className="soundpack-layout">
          <div className="soundpack-main">
            <PackHeader pack={MOCK_PACK} />

            <section className="pack-content">
              <h2 className="pack-content__title">Содержимое пакета</h2>
              <div className="pack-tracks-list">
                {MOCK_TRACKS.map((track) => (
                  <PackTrack key={track.id} track={track} />
                ))}
              </div>
            </section>
          </div>

          <aside className="soundpack-sidebar">
            <PackSidebar items={MOCK_RECOMMENDATIONS} />

            <section className="pack-reviews">
              <h3 className="pack-reviews__title">Отзывы</h3>
              {MOCK_REVIEWS.map((review) => (
                <PackReview key={review.id} review={review} />
              ))}
            </section>
          </aside>
        </div>
      </div>
    </div>
  );
}

export default SoundPackPage;
