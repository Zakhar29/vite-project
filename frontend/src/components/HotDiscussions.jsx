import DiscussionCard from "./DiscussionCard";
import SectionTitle from "./SectionTitle";
import "../styles/hotDiscussions.css";

function HotDiscussions() {
  const discussions = [
    "В этом ремиксе все по-другому!",
    "Лучший альбом года?",
    "Стоит ли возвращать винил?",
  ];

  return (
    <section className="hot-section">
      <div class = "title_hot"><SectionTitle title="Горячие обсуждения" /></div>

      <div className="hot-grid">
        {discussions.map((item, index) => (
          <DiscussionCard key={index} text={item} />
        ))}
      </div>
    </section>
  );
}

export default HotDiscussions;