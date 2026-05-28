// components/PostCard.jsx
function PostCard({ post }) {
  // Если post передан как пропс, используем его, иначе статические данные (для обратной совместимости)
  const { text, reactions, commentsCount } = post || {
    text: "Скоро будет дроп !!!",
    reactions: ["🔥", "👽"],
    commentsCount: 34
  };

  return (
    <div className="post-card">
      <div className="post-top">
        <p>{text}</p>
        <button className="edit-post">✏</button>
      </div>
      <div className="post-actions">
        {reactions.map((emoji, idx) => (
          <span key={idx}>{emoji}</span>
        ))}
      </div>
      <div className="post-footer">
        <span>💬 {commentsCount} комментария</span>
        <span>🔗</span>
      </div>
    </div>
  );
}

export default PostCard;