// components/CreatePostModal.jsx
import { useState } from 'react';
import '../styles/createPostModal.css';

const AVAILABLE_REACTIONS = ['🔥', '❤️', '👽', '🎧', '💿', '✨', '🎸', '🕹️', '👍', '😎'];

function CreatePostModal({ isOpen, onClose, onPostCreated }) {
  const [text, setText] = useState('');
  const [selectedReactions, setSelectedReactions] = useState(['🔥', '👽']); // по умолчанию выбраны

  const toggleReaction = (emoji) => {
    setSelectedReactions(prev =>
      prev.includes(emoji)
        ? prev.filter(e => e !== emoji)
        : [...prev, emoji]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    const newPost = {
      id: Date.now(),
      text: text,
      reactions: selectedReactions,
      commentsCount: 0,
      date: new Date().toISOString()
    };

    onPostCreated(newPost);
    setText('');
    setSelectedReactions(['🔥', '👽']); // сброс после отправки
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content neon-border" onClick={(e) => e.stopPropagation()}>
        <h3 className="modal-title">✨ Создать пост</h3>
        <form onSubmit={handleSubmit}>
          <textarea
            className="post-textarea neon-textarea"
            placeholder="Что у вас нового? Например: «Скоро будет дроп !!!»"
            rows="4"
            value={text}
            onChange={(e) => setText(e.target.value)}
            autoFocus
          />

          <div className="reactions-picker">
            <label>Выберите реакции (можно несколько):</label>
            <div className="emoji-grid">
              {AVAILABLE_REACTIONS.map(emoji => (
                <span
                  key={emoji}
                  className={`emoji-option ${selectedReactions.includes(emoji) ? 'active' : ''}`}
                  onClick={() => toggleReaction(emoji)}
                >
                  {emoji}
                </span>
              ))}
            </div>
            {selectedReactions.length > 0 && (
              <div className="selected-reactions">
                Выбрано: {selectedReactions.join(' ')}
              </div>
            )}
          </div>

          <div className="modal-actions">
            <button type="submit" className="neon-btn-small">Опубликовать</button>
            <button type="button" onClick={onClose} className="cancel-btn-small">Отмена</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreatePostModal;