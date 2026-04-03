import DiscussionPost from "../components/DiscussionPost";
import Comment from "../components/Comment";
import CommentForm from "../components/CommentForm";
import RelatedSidebar from "../components/RelatedSidebar";
import "../styles/thread.css";

function DiscussionThread() {
  return (
    <div className="thread-page">

      <div className="thread-layout">

        <div className="thread-main">

          <DiscussionPost />

          <CommentForm />

          <h3 className="comments-title">Комментарии</h3>

          <Comment />
          <Comment />
          <Comment />

        </div>

        <RelatedSidebar />

      </div>

    </div>
  );
}

export default DiscussionThread;