import { useState } from 'react';
import DiscussionCardd from "../components/DiscussionCardd";
import GenreSidebar from "../components/GenreSidebar";
import CreatePost from "../components/CreatePost";   // ← Добавь импорт
import "../styles/discussions.css";

function Discussions() {
  const [showCreatePost, setShowCreatePost] = useState(false);

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
          <div className="discussion-list-header">
            <h2>Дискуссии</h2>
            <button 
              className="add-post-btn"
              onClick={() => setShowCreatePost(true)}
            >
              + Добавить пост
            </button>
          </div>

          <DiscussionCardd />
          <DiscussionCardd />
          <DiscussionCardd />
        </div>
      </div>

      {/* Модальное окно создания поста */}
      <CreatePost 
        isOpen={showCreatePost} 
        onClose={() => setShowCreatePost(false)} 
      />
    </div>
  );
}

export default Discussions;