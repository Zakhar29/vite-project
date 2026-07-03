const DEFAULT_AVATAR = "/default-avatar.svg";

const BROKEN_AVATAR_PATTERNS = [
  "/static/default-avatar.png",
  "/default-avatar.png",
  "default-avatar.png",
];

export function resolveAvatarUrl(url) {
  if (!url || typeof url !== "string") {
    return DEFAULT_AVATAR;
  }

  const trimmed = url.trim();
  if (!trimmed) {
    return DEFAULT_AVATAR;
  }

  if (BROKEN_AVATAR_PATTERNS.some((pattern) => trimmed.includes(pattern))) {
    return DEFAULT_AVATAR;
  }

  if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
    return trimmed;
  }

  if (trimmed.startsWith("/static/")) {
    return DEFAULT_AVATAR;
  }

  return trimmed;
}

export function onAvatarError(event) {
  const img = event.currentTarget;
  if (img.dataset.fallbackApplied === "true") {
    return;
  }
  img.dataset.fallbackApplied = "true";
  img.src = DEFAULT_AVATAR;
}

export { DEFAULT_AVATAR };
