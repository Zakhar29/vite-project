import MusicCard from "./MusicCard";
import SectionTitle from "./SectionTitle";
import "../styles/newReleases.css";

function NewReleases() {
  const music = [
    {
      image: "https://picsum.photos/400/400?1",
      title: "Echoes of Dawn",
      artist: "Luna Rhapsody",
      type: "Album",
      year: "2024",
    },
    {
      image: "https://picsum.photos/400/400?2",
      title: "Neon Dreams",
      artist: "Synthwave Siren",
      type: "EP",
      year: "2024",
    },
    {
      image: "https://picsum.photos/400/400?3",
      title: "Starlight Symphony",
      artist: "Cosmic Harmonies",
      type: "Single",
      year: "2024",
    },
    {
      image: "https://picsum.photos/400/400?4",
      title: "Urban Pulse",
      artist: "City Beats Collective",
      type: "Album",
      year: "2024",
    },
    {
      image: "https://picsum.photos/400/400?5",
      title: "Lost in Reverie",
      artist: "Dream Weaver",
      type: "Album",
      year: "2024",
    },
    {
      image: "https://picsum.photos/400/400?6",
      title: "Chromatic Scale",
      artist: "Melody Maverick",
      type: "EP",
      year: "2024",
    },
    {
      image: "https://picsum.photos/400/400?7",
      title: "Groove Garden",
      artist: "Rhythm Keepers",
      type: "Album",
      year: "2024",
    },
    {
      image: "https://picsum.photos/400/400?8",
      title: "Silent Serenade",
      artist: "Mystic Echoes",
      type: "Single",
      year: "2024",
    },
  ];

  return (
    <section className="new-section">
      <div className="new-header">
        <SectionTitle title="Новинки" />
        <a href="#" className="view-all">Посмотреть всё →</a>
      </div>

      <div className="new-grid">
        {music.map((item, index) => (
          <MusicCard key={index} {...item} />
        ))}
      </div>
    </section>
  );
}

export default NewReleases;