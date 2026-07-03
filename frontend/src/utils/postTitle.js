export function getPostTitle(post) {
  if (post?.title?.trim()) {
    return post.title.trim();
  }

  const text = post?.text?.trim();
  if (!text) {
    return "Обсуждение";
  }

  const firstLine = text.split("\n")[0].trim();
  if (firstLine.length <= 120) {
    return firstLine;
  }

  return `${firstLine.slice(0, 117)}...`;
}
