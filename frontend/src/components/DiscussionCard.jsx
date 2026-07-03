import { Link } from "react-router-dom";
import Avatar from "./Avatar";
import { getPostTitle } from "../utils/postTitle";
import { formatCommentsLabel } from "../utils/formatComments";
import "../styles/discussionCard.css";

function DiscussionCard({ post, onClick, variant = "default" }) {
  const handleClick = () => {
    if (onClick) {
      onClick(post.id);
    }
  };

  const title = getPostTitle(post);
  const commentsLabel = formatCommentsLabel(post.comments_quantity);

  if (variant === "hot") {
    return (
      <div className="discussion-card discussion-card--hot" onClick={handleClick}>
        <h3 className="discussion-card-title">{title}</h3>
      </div>
    );
  }

  return (
    <div className="discussion-card" onClick={handleClick}>
      <div className="discussion-card-content">
        <h3 className="discussion-card-title">{title}</h3>

        {post.text && (
          <p className="discussion-card-text">
            {post.text.length > 200 ? `${post.text.slice(0, 200)}...` : post.text}
          </p>
        )}

        {post.media && post.media.length > 0 && (
          <div className="discussion-card-media-preview">
            {post.media.slice(0, 2).map((media, index) => (
              media.type === "image" ? (
                <img
                  key={index}
                  src={media.url}
                  alt=""
                  className="media-preview-image"
                />
              ) : media.type === "video" ? (
                <div key={index} className="media-preview-video">
                  Видео
                </div>
              ) : null
            ))}
            {post.media.length > 2 && (
              <span className="media-more">+{post.media.length - 2}</span>
            )}
          </div>
        )}

        <div className="discussion-card-meta">
          <div className="meta-left">
            {post.author && (
              <Link
                to={`/profile/${post.author.id}`}
                className="author-link"
                onClick={(e) => e.stopPropagation()}
              >
                <Avatar
                  src={post.author.avatar_url}
                  alt={post.author.nickname}
                  className="author-avatar-small"
                />
                <span className="author-name">{post.author.nickname}</span>
              </Link>
            )}
            <span className="post-date">{post.created_at}</span>
          </div>
        </div>

        <div className="discussion-card-footer">
          <span className="discussion-card-stat">♥ {post.likes_quantity || 0}</span>
          <span className="discussion-card-stat">💬 {commentsLabel}</span>
        </div>
      </div>
    </div>
  );
}

export default DiscussionCard;
