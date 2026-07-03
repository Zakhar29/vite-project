import "../styles/hero.css";
import heroImg from "../assets/i.webp";

function Hero() {
  return (
    <section className="hero">
      <img src={heroImg} alt="Концерт" className="hero__image" />
      <div className="hero__content">
        <h1>
          Расслабьтесь с тщательно подобранной подборкой талантливых
          музыкантов и принимайте участие в обсуждениях, а также темах
        </h1>
      </div>
    </section>
  );
}

export default Hero;
