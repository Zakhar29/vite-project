import { resolveAvatarUrl, onAvatarError } from "../utils/avatar";

function Avatar({ src, alt = "", className = "", ...props }) {
  return (
    <img
      src={resolveAvatarUrl(src)}
      alt={alt}
      className={className}
      onError={onAvatarError}
      loading="lazy"
      {...props}
    />
  );
}

export default Avatar;
