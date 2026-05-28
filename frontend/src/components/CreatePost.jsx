import { useState } from 'react';
import '../styles/createPost.css';

function CreatePost({ isOpen, onClose }) {
  const [title, setTitle] = useState('');
  const [text, setText] = useState('');
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isPublished, setIsPublished] = useState(false);

  if (!isOpen) return null;

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handlePublish = () => {
    if (!title.trim() && !text.trim()) return;

    setIsPublished(true);

    console.log('📤 Новый пост:', { title, text, image });

    setTimeout(() => {
      setIsPublished(false);
      setTitle('');
      setText('');
      setImage(null);
      setImagePreview(null);
      onClose();
    }, 1200);
  };

  return (
    <div className="create-post-overlay">
      <div className="create-post-modal">
        {/* Header */}
        <div className="create-post-header">
          <div className="user-info">
            <div className="avatar">
              <img src="https://i.pravatar.cc/48" alt="User" />
            </div>
            <div>
              <p>Egor</p>
              <span className="time">только что</span>
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {/* Заголовок */}
        <div className="create-post-title">
          <input
            type="text"
            placeholder="Заголовок"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        {/* Фото */}
        <div className="create-post-photo">
          <label className="photo-upload-area">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              hidden
            />
            {imagePreview ? (
              <img src={imagePreview} alt="preview" className="image-preview" />
            ) : (
              <div className="upload-placeholder">
                <span className="upload-icon">📷</span>
                <p>Загрузить фото</p>
              </div>
            )}
          </label>
        </div>

        {/* Текст */}
        <div className="create-post-text">
          <textarea
            placeholder="Текст"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>

        {/* Footer */}
        <div className="create-post-footer">
          <div className="made-with">
            Made with <span className="violet">V</span>
          </div>

          <div className="footer-right">
            {isPublished && <span className="saved-text">✅ Сохранено</span>}
            <button
              className="publish-btn"
              onClick={handlePublish}
              disabled={!title.trim() && !text.trim()}
            >
              Опубликовать
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CreatePost;