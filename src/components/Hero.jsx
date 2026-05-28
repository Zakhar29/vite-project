import "../styles/hero.css";
import heroImg from "../assets/i.webp"; // сюда потом положишь картинку

function Hero() {
  return (
    <section className="hero">
      <img src={heroImg} alt="concert" className="hero__image" />

      <div className="hero__content">
        <h1>
          Расслабьтесь с тщательно подобранной и подборкой талантливых
          музыкантов и принимайте участие в обсуждениях
        </h1>
      </div>
    </section>
  );
}

export default Hero;