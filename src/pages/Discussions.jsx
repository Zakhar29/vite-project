import DiscussionCard from "../components/DiscussionCardd";
import GenreSidebar from "../components/GenreSidebar";
import "../styles/discussions.css";

function Discussions() {
  return (
    <div className="discussions-page">

      {/* HERO */}
      <div className="discussion-hero">

        <div className="hero-text">
          <h1>
            Погружение в сердце звука:
            дискуссия "Возрождение синтезаторных волн"
          </h1>

          <p>
            Познакомьтесь с возрождением электронной музыки 80-х.
            Поделитесь любимыми треками и обсудите методы продюсирования.
          </p>

          <button>Присоединиться к дискуссии</button>
        </div>

        <img
          src="https://picsum.photos/500/300"
          alt="sound wave"
        />

      </div>

      {/* MAIN CONTENT */}
      <div className="discussion-content">

        <GenreSidebar />

        <div className="discussion-list">

          <h2>Дискуссии</h2>

          <DiscussionCard />
          <DiscussionCard />
          <DiscussionCard />

        </div>

      </div>

    </div>
  );
}

export default Discussions;