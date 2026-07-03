import Hero from "../components/Hero";
import HotDiscussions from "../components/HotDiscussions";
import NewReleases from "../components/NewReleases";
import ForYou from "../components/ForYou";
import "../styles/home.css";

function Home() {
  return (
    <div className="home-page">
      <div className="home-page__inner">
        <Hero />
        <HotDiscussions />
        <NewReleases />
        <ForYou />
      </div>
    </div>
  );
}

export default Home;