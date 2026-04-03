import SoundCard from "../components/SoundCard";
import "../styles/soundpacks.css";

function SoundPacks() {
  return (
    <div className="soundpacks-page">

      {/* HERO */}
      <div className="soundpacks-hero">

        <div className="hero-text">
          <h1>
            Откройте для себя свой звук:
            Изучите тысячи сэмплов,
            пресетов и наборов
          </h1>

          <p>
            Воспользуйтесь нашей тщательно отобранной библиотекой
            высококачественных звуков.
          </p>

          <button>Изучите нашу библиотеку</button>
        </div>

        <img
          src="https://picsum.photos/500/300"
          alt="wave"
        />

      </div>

      {/* FILTER BAR */}
      <div className="soundpacks-controls">

        <div className="tabs">
          <button className="active">Семплы</button>
          <button>Пресеты</button>
          <button>Киты</button>
        </div>

        <input
          className="search"
          placeholder="Найти семпл, пресет..."
        />

      </div>

      {/* CARDS */}
      <div className="soundpacks-grid">

        <SoundCard />
        <SoundCard />
        <SoundCard />

      </div>

    </div>
  );
}

export default SoundPacks;