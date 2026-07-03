import { useState } from "react";
import "../styles/discussions.css";

const GENRES = [
  { id: "electronic", label: "Электронная", icon: "⚡" },
  { id: "rock", label: "Рок", icon: "🎸" },
  { id: "hiphop", label: "Хип-хоп", icon: "🎧" },
  { id: "pop", label: "Поп", icon: "♥" },
  { id: "classical", label: "Классическая", icon: "🎻" },
];

const FILTERS = [
  { id: "trending", label: "В тренде", icon: "🔥" },
  { id: "new", label: "Новое", icon: "✨" },
  { id: "mine", label: "Моё", icon: "👤" },
];

function GenreSidebar({ activeGenre, activeFilter, onGenreChange, onFilterChange }) {
  return (
    <aside className="genre-sidebar">
      <h3 className="genre-sidebar__title">ЖАНРЫ</h3>

      <ul className="genre-sidebar__list">
        {GENRES.map((genre) => (
          <li key={genre.id}>
            <button
              type="button"
              className={`genre-sidebar__item ${activeGenre === genre.id ? "active" : ""}`}
              onClick={() => onGenreChange?.(genre.id)}
            >
              <span className="genre-sidebar__item-left">
                <span className="genre-sidebar__icon">{genre.icon}</span>
                {genre.label}
              </span>
              <span className="genre-sidebar__chevron">›</span>
            </button>
          </li>
        ))}
      </ul>

      <div className="genre-sidebar__filters">
        {FILTERS.map((filter) => (
          <button
            key={filter.id}
            type="button"
            className={`genre-sidebar__filter ${activeFilter === filter.id ? "active" : ""}`}
            onClick={() => onFilterChange?.(filter.id)}
          >
            <span>{filter.icon}</span>
            {filter.label}
          </button>
        ))}
      </div>
    </aside>
  );
}

export default GenreSidebar;
