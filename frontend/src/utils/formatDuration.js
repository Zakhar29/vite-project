export function formatTrackDuration(seconds) {
  if (seconds == null || Number.isNaN(seconds)) return "—";
  const total = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(total / 60);
  const secs = total % 60;
  return `${minutes}:${secs.toString().padStart(2, "0")}`;
}

export function formatTotalDurationLabel(trackCount, totalSeconds) {
  if (!trackCount) return "0 треков";
  const tracksLabel = `${trackCount} ${trackCount === 1 ? "трек" : trackCount < 5 ? "трека" : "треков"}`;
  if (!totalSeconds) return tracksLabel;
  const minutes = Math.max(1, Math.round(totalSeconds / 60));
  return `${tracksLabel} • ${minutes} мин`;
}

export function estimateTrackDuration(track) {
  if (track?.duration_seconds) return track.duration_seconds;
  if (track?.duration) return track.duration;
  // Placeholder until backend provides duration
  const seed = String(track?.track_id || track?.id || track?.title || "").length;
  return 180 + (seed % 120);
}
