
import Home from "./pages/Home";
import Track from "./pages/Track";
import Settings from "./pages/Settings";
import Album from "./pages/Album";
import Playlist from "./pages/Playlist";
import Navbar from "./components/Navbar";
import Discussions from "./pages/Discussions";
import DiscussionThread from "./pages/DiscussionThread";
import SoundPacks from "./pages/SoundPacks";
import SoundPackPage from "./pages/SoundPackPage";
import Profile from "./pages/Profile";
import Subscription from "./pages/Subscription";
import Notifications from "./pages/Notifications";
import Login from "./pages/Login";
import { Routes, Route } from "react-router-dom";
function App() {
  return (
    <>
    <Navbar />
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/track/:id" element={<Track />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/album/:id" element={<Album />} />
      <Route path="/playlist/:id" element={<Playlist />} />
      <Route path="/discussions" element={<Discussions />} />
      <Route path="/discussion/:id" element={<DiscussionThread />} />
      <Route path="/soundpacks" element={<SoundPacks />} />
      <Route path="/soundpack/:id" element={<SoundPackPage />} />
      <Route path="/profile/:id" element={<Profile />} />
      <Route path="/subscription" element={<Subscription />} />
      <Route path="/notifications" element={<Notifications />} />
      <Route path="/login" element={<Login />} />
    </Routes>
    </>
  );
}

export default App;