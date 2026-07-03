import { useNavigate } from "react-router-dom";
import Avatar from "./Avatar";

function formatDate(dateStr) {
  if (!dateStr) return "недавно";
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000 / 60);
    if (diff < 60) return `${Math.max(diff, 1)} мин назад`;
    if (diff < 1440) return `${Math.floor(diff / 60)} ч назад`;
    return date.toLocaleDateString("ru-RU", { day: "numeric", month: "long" });
  } catch {
    return dateStr;
  }
}

function TrackComment({ comment }) {
  const navigate = useNavigate();

  return (
    <article className="track-comment">
      <Avatar
        src={comment.author?.avatar_url}
        alt={comment.author?.nickname}
        className="track-comment__avatar"
        onClick={() => navigate(`/profile/${comment.author?.id}`)}
      />
      <div className="track-comment__body">
        <div className="track-comment__meta">
          <b onClick={() => navigate(`/profile/${comment.author?.id}`)}>
            {comment.author?.nickname || "Пользователь"}
          </b>
          <span>{comment.created_at_formatted || formatDate(comment.created_at)}</span>
        </div>
        <p>{comment.comment}</p>
        <div className="track-comment__actions">
          <button type="button">↩ Ответить</button>
          <button type="button">♥ {comment.likes_quantity || 0}</button>
          <button type="button" className="track-comment__more">⋯</button>
        </div>
      </div>
    </article>
  );
}

export default TrackComment;
