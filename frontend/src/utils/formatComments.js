export function formatCommentsLabel(count) {
  const n = Number(count) || 0;
  const mod10 = n % 10;
  const mod100 = n % 100;

  let word = "комментариев";
  if (mod10 === 1 && mod100 !== 11) {
    word = "комментарий";
  } else if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
    word = "комментария";
  }

  return `${n} ${word}`;
}
