
import Hero from "../components/Hero";
import HotDiscussions from "../components/HotDiscussions";
import NewReleases from "../components/NewReleases";
import ForYou from "../components/ForYou";
import "../styles/home.css";
function Home() {
  return (
    <div className="home_page">
  
      <Hero />
      <HotDiscussions />
      <NewReleases />
      <ForYou />
    </div>
  );
}

export default Home;