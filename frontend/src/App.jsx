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
import ProfileEdit from "./pages/ProfileEdit";
import UploadTrack from "./pages/UploadTrack";
import Premium from "./pages/Premium";
import Register from "./pages/Register";
import Chat from "./pages/Chat";
import BottomPlayer from "./components/BottomPlayer";
import CreateRelease from "./pages/CreateRelease";
import Search from "./pages/Search"; // ← ИМПОРТ СТРАНИЦЫ ПОИСКА

function App() {
  return (
    <>
      <Navbar />
      <BottomPlayer />

      <Routes>
        {/* Главная страница */}
        <Route path="/" element={<Home />} />

        {/* Страница отдельного трека */}
        <Route path="/track/:id" element={<Track />} />

        {/* Настройки пользователя */}
        <Route path="/settings" element={<Settings />} />

        {/* Страница альбома */}
        <Route path="/album/:id" element={<Album />} />

        {/* Страница плейлиста */}
        <Route path="/playlist/:id" element={<Playlist />} />

        {/* Список всех дискуссий */}
        <Route path="/discussions" element={<Discussions />} />

        {/* Конкретная дискуссия / тред */}
        <Route path="/discussion/:id" element={<DiscussionThread />} />

        {/* Каталог звуковых пакетов */}
        <Route path="/soundpacks" element={<SoundPacks />} />

        {/* Страница отдельного звукового пакета */}
        <Route path="/soundpack/:id" element={<SoundPackPage />} />

        {/* Профиль пользователя */}
        <Route path="/profile/:id" element={<Profile />} />

        {/* Страница оформления подписки */}
        <Route path="/subscription" element={<Subscription />} />

        {/* Уведомления */}
        <Route path="/notifications" element={<Notifications />} />

        {/* Страница входа */}
        <Route path="/login" element={<Login />} />

        {/* Страница редактирования профиля */}
        <Route path="/profile/edit" element={<ProfileEdit />} />

        {/* Загрузка трека */}
        <Route path="/upload-track" element={<UploadTrack />} />

        {/* Создание релиза (Сингл / EP / Альбом) */}
        <Route path="/create-release" element={<CreateRelease />} />

        {/* Страница подписки */}
        <Route path="/premium" element={<Premium />} />

        {/* Страница регистрации */}
        <Route path="/register" element={<Register />} />

        {/* Чат / Сообщество */}
        <Route path="/chat" element={<Chat />} />

        {/* ===== СТРАНИЦА ПОИСКА ===== */}
        <Route path="/search" element={<Search />} />
      </Routes>
    </>
  );
}

export default App;