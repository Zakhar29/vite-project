import { Link } from "react-router-dom";

function PlayIcon() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <path fill="currentColor" d="M8 5v14l11-7z" />
    </svg>
  );
}

function ShuffleIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M16 3h5v5M4 20 21 3M21 16v5h-5M15 15l6 6M4 4l5 5"
      />
    </svg>
  );
}

function HeartIcon({ filled }) {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <path
        fill={filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.8"
        d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2 4 4 0 0 1 7 2c0 5.5-7 10-7 10z"
      />
    </svg>
  );
}

function CollectionHeader({
  coverUrl,
  title,
  subtitle,
  subtitleTo,
  description,
  metaLabel,
  onPlay,
  onShuffle,
  onLike,
  isLiked = false,
  canPlay = true,
}) {
  return (
    <section className="collection-hero">
      <img
        src={coverUrl || "https://picsum.photos/400/400?album"}
        className="collection-hero__cover"
        alt={title}
      />

      <div className="collection-hero__body">
        <h1 className="collection-hero__title">{title}</h1>

        {subtitleTo ? (
          <Link to={subtitleTo} className="collection-hero__subtitle">
            {subtitle}
          </Link>
        ) : (
          <p className="collection-hero__subtitle">{subtitle}</p>
        )}

        {description && (
          <p className="collection-hero__desc">{description}</p>
        )}

        {metaLabel && (
          <p className="collection-hero__meta">{metaLabel}</p>
        )}

        <div className="collection-hero__actions">
          <button
            type="button"
            className="collection-hero__play"
            onClick={onPlay}
            disabled={!canPlay}
          >
            <PlayIcon />
            Воспроизвести
          </button>

          <button
            type="button"
            className="collection-hero__shuffle"
            onClick={onShuffle}
            disabled={!canPlay}
          >
            <ShuffleIcon />
            Перемешать
          </button>

          {onLike && (
            <button
              type="button"
              className={`collection-hero__icon-btn ${isLiked ? "is-active" : ""}`}
              onClick={onLike}
              aria-label="Нравится"
            >
              <HeartIcon filled={isLiked} />
            </button>
          )}

          <button
            type="button"
            className="collection-hero__icon-btn"
            aria-label="Ещё"
          >
            ⋯
          </button>
        </div>
      </div>
    </section>
  );
}

export default CollectionHeader;
