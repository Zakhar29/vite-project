import { useState, useEffect} from "react";
import { Link } from "react-router-dom";
import ProfileHeader from "../components/ProfileHeader";
import PlaylistCard from "../components/PlaylistCard";
import AlbumCard from "../components/AlbumCard";
import ProfileTrack from "../components/ProfileTrack";
import PostCard from "../components/PostCard";
import CreatePostModal from "../components/CreatePostModal";

import "../styles/profile.css";

function Profile() {

const [tab, setTab] = useState("wall");
const [posts, setPosts] = useState([]);
  // 🎵 Состояния для хранения альбомов и синглов
  const [albums, setAlbums] = useState([]);
  const [singles, setSingles] = useState([]);
const [isModalOpen, setIsModalOpen] = useState(false);
 // Загружаем посты из localStorage при монтировании
    useEffect(() => {
      const savedPosts = localStorage.getItem("userPosts");
      if (savedPosts) {
        setPosts(JSON.parse(savedPosts));
      } else {
        // Начальные посты для примера (можно оставить или удалить)
        const defaultPosts = [
          {
            id: 1,
            text: "Скоро будет дроп !!!",
            reactions: ["🔥", "👽"],
            commentsCount: 34,
            date: "2025-01-15T10:00:00Z"
          },
          {
            id: 2,
            text: "Новый трек уже в процессе...",
            reactions: ["🔥", "👽"],
            commentsCount: 12,
            date: "2025-01-10T15:30:00Z"
          }
        ];
        setPosts(defaultPosts);
        localStorage.setItem("userPosts", JSON.stringify(defaultPosts));
      }
    }, []);

  // Сохраняем посты в localStorage при изменении
  useEffect(() => {
    if (posts.length > 0) {
      localStorage.setItem("userPosts", JSON.stringify(posts));
    }
  }, [posts]);

  const handlePostCreated = (newPost) => {
    setPosts(prev => [newPost, ...prev]);
  };

return (
<div className="profile-page">

<ProfileHeader />
 <div className="profile-edit-link">
      <Link to="/profile/edit" className="edit-profile-btn neon-btn-small">✎ Редактировать профиль</Link>
      <Link to="/upload-track" className="upload-track-btn neon-btn-small">🎵 + Загрузить трек</Link>
      <Link to="/create-release" className="create-release-btn neon-btn-small">➕ Создать релиз</Link>

    </div>


<div className="profile-tabs">

<span
className={tab === "wall" ? "active" : ""}
onClick={() => setTab("wall")}
>
Плейлисты/Треки
</span>

<span
className={tab === "posts" ? "active" : ""}
onClick={() => setTab("posts")}
>
Посты
</span>

</div>

{/* СТЕНА */}
{tab === "wall" && (
<>

<h2>Плейлисты</h2>

<div className="playlist-row">
<PlaylistCard />
<PlaylistCard />
<PlaylistCard />
</div>

<h2>Альбомы</h2>

<div className="album-row">
{albums.map(album => (
    <AlbumCard key={album.id} album={album} />
  ))}
</div>

<h2>Треки</h2>

<div className="tracks-list">
<ProfileTrack />
<ProfileTrack />
</div>

</>
)}

{/* ПОСТЫ */}
{tab === "posts" && (
<div className="posts-section">

<div className="posts-header">
<h2>Посты</h2>
<button className="add-post" onClick={() => setIsModalOpen(true)}>+</button>
</div>

{posts.map(post => (
            <PostCard key={post.id} post={post} />
          ))}

<PostCard />
<PostCard />
<PostCard />
<PostCard />

</div>
)}  
<CreatePostModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onPostCreated={handlePostCreated}
      />
    
</div>


);
}

export default Profile;