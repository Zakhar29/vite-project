import MusicCard from "./MusicCard";
import SectionTitle from "./SectionTitle";
import "../styles/forYou.css";

function ForYou() {
  const recommendations = [
    {
      image: "https://picsum.photos/400/400?11",
      title: "Midnight Waves",
      artist: "Ocean Drive",
      type: "Album",
      year: "2024",
    },
    {
      image: "https://picsum.photos/400/400?12",
      title: "Electric Horizon",
      artist: "Nova Pulse",
      type: "Single",
      year: "2024",
    },
    {
      image: "https://picsum.photos/400/400?13",
      title: "Velvet Nights",
      artist: "Soul Whisper",
      type: "EP",
      year: "2024",
    },
    {
      image: "https://picsum.photos/400/400?14",
      title: "Golden Frequency",
      artist: "Aurora Beat",
      type: "Album",
      year: "2024",
    },
  ];

  return (
    <section className="foryou-section">
      <SectionTitle title="Для вас" />

      <div className="foryou-grid">
        {recommendations.map((item, index) => (
          <MusicCard key={index} {...item} />
        ))}
      </div>
    </section>
  );
}

export default ForYou;