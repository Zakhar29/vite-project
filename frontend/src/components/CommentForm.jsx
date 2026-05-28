function CommentForm() {
  return (
    <div className="comment-form">

      <h3>Добавить комментарий</h3>

      <textarea
        placeholder="Написать комментарий..."
      />

      <button>Отправить</button>

    </div>
  );
}

export default CommentForm;