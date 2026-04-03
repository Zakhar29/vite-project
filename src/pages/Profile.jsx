import { useState } from "react";

import ProfileHeader from "../components/ProfileHeader";
import PlaylistCard from "../components/PlaylistCard";
import AlbumCard from "../components/AlbumCard";
import ProfileTrack from "../components/ProfileTrack";
import PostCard from "../components/PostCard";

import "../styles/profile.css";

function Profile() {

const [tab, setTab] = useState("wall");

return (
<div className="profile-page">

<ProfileHeader />

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
<AlbumCard />
<AlbumCard />
<AlbumCard />
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
<button className="add-post">+</button>
</div>

<PostCard />
<PostCard />
<PostCard />
<PostCard />

</div>
)}

</div>
);
}

export default Profile;