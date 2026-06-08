# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

# Запуск
``` docker-compose up --build ```


# Навигация по страницам
Список страниц с их Route(взято из файла App.jsx ; путь к файлу: /frontend/src/App.jsx) :

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
    </Routes>
    </>
