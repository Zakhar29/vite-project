import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import "../styles/search.css";

// ========== Конфигурация API ==========
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

// ========== Простая debounce функция ==========
function useDebounce(callback, delay) {
  const timeoutRef = useRef(null);

  return useCallback((...args) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  }, [callback, delay]);
}

function Search() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const token = localStorage.getItem("access_token");

  // ========== Состояния ==========
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [activeTab, setActiveTab] = useState('all');
  const [results, setResults] = useState({
    users: { items: [], total: 0 },
    tracks: { items: [], total: 0 },
    albums: { items: [], total: 0 },
    posts: { items: [], total: 0 }
  });
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [error, setError] = useState(null);

  // ========== Фильтры ==========
  const [filters, setFilters] = useState({
    genres: [],
    albumTypes: [],
    bpmMin: '',
    bpmMax: '',
    sortBy: 'relevance',
    sortOrder: 'desc'
  });

  // ========== Справочные данные ==========
  const [genres, setGenres] = useState([]);
  const [albumTypes, setAlbumTypes] = useState([]);
  const [loadingFilters, setLoadingFilters] = useState(true);

  // ========== Загрузка справочных данных ==========

  useEffect(() => {
    const queryParam = searchParams.get('q');
    if (queryParam && queryParam.trim()) {
      setQuery(queryParam);
      performSearch(queryParam, activeTab, 0);
    } else if (!queryParam) {
      setQuery('');
      setResults({ users: { items: [], total: 0 }, tracks: { items: [], total: 0 }, albums: { items: [], total: 0 }, posts: { items: [], total: 0 } });
    }
  }, [searchParams, activeTab]);

  const loadFormData = async () => {
    try {
      setLoadingFilters(true);
      const response = await fetch(`${API_URL}/api/v1/new_album/create-form-data`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      if (!response.ok) throw new Error('Ошибка загрузки данных');

      const data = await response.json();
      setGenres(data.genres || []);
      setAlbumTypes(data.album_types || []);
    } catch (err) {
      console.error('Ошибка загрузки фильтров:', err);
    } finally {
      setLoadingFilters(false);
    }
  };

  // ========== Поиск ==========

  const performSearch = useCallback(async (searchQuery, tab, skipValue = 0) => {
    if (!searchQuery.trim()) {
      setResults({ users: { items: [], total: 0 }, tracks: { items: [], total: 0 }, albums: { items: [], total: 0 }, posts: { items: [], total: 0 } });
      setHasMore(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Для всех категорий используем /all
      if (tab === 'all') {
        const response = await fetch(
          `${API_URL}/api/v1/search/all?query=${encodeURIComponent(searchQuery)}&skip=${skipValue}&limit=${limit}`,
          { headers: token ? { Authorization: `Bearer ${token}` } : {} }
        );

        if (!response.ok) throw new Error('Ошибка поиска');

        const data = await response.json();
        setResults({
          users: data.users || { items: [], total: 0 },
          tracks: data.tracks || { items: [], total: 0 },
          albums: data.albums || { items: [], total: 0 },
          posts: data.posts || { items: [], total: 0 }
        });
        setHasMore(false);
      } else {
        // Поиск по конкретной категории
        let endpoint = '';
        let params = new URLSearchParams();
        params.append('query', searchQuery);
        params.append('skip', skipValue);
        params.append('limit', limit);

        if (tab === 'users') {
          endpoint = '/api/v1/search/users';
        } else if (tab === 'tracks') {
          endpoint = '/api/v1/search/tracks';
          if (filters.genres.length > 0) {
            params.append('genre_ids', filters.genres.join(','));
          }
          if (filters.bpmMin) params.append('bpm_min', filters.bpmMin);
          if (filters.bpmMax) params.append('bpm_max', filters.bpmMax);
          params.append('sort_by', filters.sortBy);
          params.append('sort_order', filters.sortOrder);
        } else if (tab === 'albums') {
          endpoint = '/api/v1/search/albums';
          if (filters.genres.length > 0) {
            params.append('genre_ids', filters.genres.join(','));
          }
          if (filters.albumTypes.length > 0) {
            params.append('album_type', filters.albumTypes[0]);
          }
          params.append('sort_by', filters.sortBy);
          params.append('sort_order', filters.sortOrder);
        } else if (tab === 'posts') {
          endpoint = '/api/v1/search/posts';
          params.append('sort_by', 'created_at');
          params.append('sort_order', 'desc');
        }

        const response = await fetch(
          `${API_URL}${endpoint}?${params.toString()}`,
          { headers: token ? { Authorization: `Bearer ${token}` } : {} }
        );

        if (!response.ok) throw new Error('Ошибка поиска');

        const data = await response.json();

        // Обновляем результаты для активной категории
        setResults(prev => ({
          ...prev,
          [tab]: {
            items: skipValue === 0 ? data.items : [...prev[tab].items, ...data.items],
            total: data.total || 0
          }
        }));

        setHasMore(data.has_more || false);
        setSkip(skipValue + limit);
      }
    } catch (err) {
      console.error('Ошибка поиска:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token, limit, filters]);

  // ========== Debounced поиск ==========

  const debouncedSearch = useDebounce((searchQuery, tab) => {
    performSearch(searchQuery, tab, 0);
  }, 500);

  // ========== АВТОМАТИЧЕСКИЙ ПОИСК ПРИ ЗАГРУЗКЕ ==========
  useEffect(() => {
    const initialQuery = searchParams.get('q');
    if (initialQuery && initialQuery.trim()) {
      setQuery(initialQuery);
      // Выполняем поиск сразу при загрузке
      performSearch(initialQuery, 'all', 0);
    }
  }, []); // Пустой массив = только при монтировании

  // ========== Обработчики ==========

  const handleSearch = (e) => {
    const value = e.target.value;
    setQuery(value);
    setSearchParams({ q: value });

    if (value.trim()) {
      debouncedSearch(value, activeTab);
    } else {
      setResults({ users: { items: [], total: 0 }, tracks: { items: [], total: 0 }, albums: { items: [], total: 0 }, posts: { items: [], total: 0 } });
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setSkip(0);
    if (query.trim()) {
      performSearch(query, tab, 0);
    }
  };

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      performSearch(query, activeTab, skip);
    }
  };

  const handleGenreChange = (genreId) => {
    setFilters(prev => {
      const newGenres = prev.genres.includes(genreId)
        ? prev.genres.filter(id => id !== genreId)
        : [...prev.genres, genreId];
      return { ...prev, genres: newGenres };
    });
  };

  const handleAlbumTypeChange = (typeId) => {
    setFilters(prev => ({
      ...prev,
      albumTypes: prev.albumTypes.includes(typeId)
        ? prev.albumTypes.filter(id => id !== typeId)
        : [typeId]
    }));
  };

  // ========== Рендер результатов ==========

  const renderResults = () => {
    if (activeTab === 'all') {
      const hasResults = results.users.total > 0 || results.tracks.total > 0 ||
                         results.albums.total > 0 || results.posts.total > 0;

      if (!hasResults && query.trim() && !loading) {
        return <div className="no-results">Ничего не найдено по запросу "{query}"</div>;
      }

      return (
        <div className="search-results-all">
          {results.users.items.length > 0 && (
            <div className="result-section">
              <h3>Пользователи ({results.users.total})</h3>
              <div className="result-grid users-grid">
                {results.users.items.map(user => (
                  <div key={user.id} className="user-result" onClick={() => navigate(`/profile/${user.id}`)}>
                    <img src={user.avatar_url || '/default-avatar.png'} alt={user.nickname} />
                    <span>{user.nickname}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {results.tracks.items.length > 0 && (
            <div className="result-section">
              <h3>Треки ({results.tracks.total})</h3>
              <div className="result-grid">
                {results.tracks.items.map(track => (
                  <div key={track.track_id} className="track-result" onClick={() => navigate(`/track/${track.track_id}`)}>
                    <img src={track.cover_url || '/default-cover.jpg'} alt={track.title} />
                    <div>
                      <div className="title">{track.title}</div>
                      <div className="artist">{track.author_nickname || 'Неизвестный'}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {results.albums.items.length > 0 && (
            <div className="result-section">
              <h3>Альбомы ({results.albums.total})</h3>
              <div className="result-grid">
                {results.albums.items.map(album => (
                  <div key={album.id} className="album-result" onClick={() => navigate(`/album/${album.id}`)}>
                    <img src={album.cover_url || '/default-cover.jpg'} alt={album.title} />
                    <div>
                      <div className="title">{album.title}</div>
                      <div className="artist">{album.author_nickname || 'Неизвестный'}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {results.posts.items.length > 0 && (
            <div className="result-section">
              <h3>Посты ({results.posts.total})</h3>
              <div className="result-grid posts-grid">
                {results.posts.items.map(post => (
                  <div key={post.id} className="post-result" onClick={() => navigate(`/discussion/${post.id}`)}>
                    <div className="post-content">
                      <div className="post-text">{post.text?.slice(0, 150)}...</div>
                      <div className="post-author">{post.author_nickname || 'Пользователь'}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    }

    // Результаты для конкретной категории
    const items = results[activeTab]?.items || [];
    const total = results[activeTab]?.total || 0;

    if (items.length === 0 && query.trim() && !loading) {
      return <div className="no-results">Ничего не найдено по запросу "{query}"</div>;
    }

    return (
      <div className="search-results-category">
        {activeTab === 'users' && (
          <div className="users-list">
            {items.map(user => (
              <div key={user.id} className="user-result-item" onClick={() => navigate(`/profile/${user.id}`)}>
                <img src={user.avatar_url || '/default-avatar.png'} alt={user.nickname} />
                <div>
                  <div className="name">{user.nickname}</div>
                  <div className="sub">{user.email || ''}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'tracks' && (
          <div className="tracks-list">
            {items.map(track => (
              <div key={track.track_id} className="track-result-item" onClick={() => navigate(`/track/${track.track_id}`)}>
                <img src={track.cover_url || '/default-cover.jpg'} alt={track.title} />
                <div>
                  <div className="title">{track.title}</div>
                  <div className="artist">{track.author_nickname || 'Неизвестный'}</div>
                  {track.bpm && <div className="meta">BPM: {track.bpm}</div>}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'albums' && (
          <div className="albums-list">
            {items.map(album => (
              <div key={album.id} className="album-result-item" onClick={() => navigate(`/album/${album.id}`)}>
                <img src={album.cover_url || '/default-cover.jpg'} alt={album.title} />
                <div>
                  <div className="title">{album.title}</div>
                  <div className="artist">{album.author_nickname || 'Неизвестный'}</div>
                  <div className="meta">{album.type || 'Альбом'} • {album.tracks_count || 0} треков</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'posts' && (
          <div className="posts-list">
            {items.map(post => (
              <div key={post.id} className="post-result-item" onClick={() => navigate(`/discussion/${post.id}`)}>
                <div className="post-content">
                  <div className="post-text">{post.text}</div>
                  <div className="post-meta">
                    <span>{post.author_nickname || 'Пользователь'}</span>
                    <span>{post.created_at_formatted || ''}</span>
                    <span>❤️ {post.likes_quantity || 0}</span>
                    <span>💬 {post.comments_quantity || 0}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {hasMore && (
          <button className="load-more" onClick={handleLoadMore} disabled={loading}>
            {loading ? 'Загрузка...' : 'Загрузить еще'}
          </button>
        )}
      </div>
    );
  };

  // ========== Рендер фильтров ==========

  const renderFilters = () => {
    if (activeTab === 'all') return null;

    return (
      <div className="search-filters">
        {activeTab === 'tracks' && (
          <>
            <div className="filter-group">
              <label>Жанры</label>
              <div className="filter-options">
                {genres.map(genre => (
                  <button
                    key={genre.id}
                    className={`filter-chip ${filters.genres.includes(genre.id) ? 'active' : ''}`}
                    onClick={() => handleGenreChange(genre.id)}
                  >
                    {genre.title}
                  </button>
                ))}
              </div>
            </div>

            <div className="filter-group">
              <label>BPM</label>
              <div className="filter-row">
                <input
                  type="number"
                  placeholder="От"
                  value={filters.bpmMin}
                  onChange={(e) => setFilters(prev => ({ ...prev, bpmMin: e.target.value }))}
                />
                <span>-</span>
                <input
                  type="number"
                  placeholder="До"
                  value={filters.bpmMax}
                  onChange={(e) => setFilters(prev => ({ ...prev, bpmMax: e.target.value }))}
                />
              </div>
            </div>

            <div className="filter-group">
              <label>Сортировка</label>
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value }))}
              >
                <option value="relevance">По релевантности</option>
                <option value="liked_quantity">По популярности</option>
                <option value="listening_quantity">По прослушиваниям</option>
                <option value="created_at">По дате</option>
              </select>
            </div>
          </>
        )}

        {activeTab === 'albums' && (
          <>
            <div className="filter-group">
              <label>Тип</label>
              <div className="filter-options">
                {albumTypes.map(type => (
                  <button
                    key={type.id}
                    className={`filter-chip ${filters.albumTypes.includes(type.id) ? 'active' : ''}`}
                    onClick={() => handleAlbumTypeChange(type.id)}
                  >
                    {type.title}
                  </button>
                ))}
              </div>
            </div>

            <div className="filter-group">
              <label>Жанры</label>
              <div className="filter-options">
                {genres.map(genre => (
                  <button
                    key={genre.id}
                    className={`filter-chip ${filters.genres.includes(genre.id) ? 'active' : ''}`}
                    onClick={() => handleGenreChange(genre.id)}
                  >
                    {genre.title}
                  </button>
                ))}
              </div>
            </div>

            <div className="filter-group">
              <label>Сортировка</label>
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value }))}
              >
                <option value="relevance">По релевантности</option>
                <option value="liked_quantity">По популярности</option>
                <option value="listening_quantity">По прослушиваниям</option>
                <option value="created_at">По дате</option>
              </select>
            </div>
          </>
        )}

        <button
          className="apply-filters"
          onClick={() => {
            setSkip(0);
            performSearch(query, activeTab, 0);
          }}
        >
          Применить фильтры
        </button>
      </div>
    );
  };

  // ========== Основной рендер ==========

  return (
    <div className="search-page">
      <div className="search-container">
        {/* Поисковая строка */}
        <div className="search-header">
          <div className="search-input-wrapper">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              className="search-input"
              placeholder="Поиск музыки, альбомов, пользователей, постов..."
              value={query}
              onChange={handleSearch}
              autoFocus
            />
            {query && (
              <button className="clear-search" onClick={() => {
                setQuery('');
                setSearchParams({});
                setResults({ users: { items: [], total: 0 }, tracks: { items: [], total: 0 }, albums: { items: [], total: 0 }, posts: { items: [], total: 0 } });
              }}>
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Вкладки */}
        <div className="search-tabs">
          <button
            className={`tab ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => handleTabChange('all')}
          >
            Все
          </button>
          <button
            className={`tab ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => handleTabChange('users')}
          >
            Пользователи
          </button>
          <button
            className={`tab ${activeTab === 'tracks' ? 'active' : ''}`}
            onClick={() => handleTabChange('tracks')}
          >
            Треки
          </button>
          <button
            className={`tab ${activeTab === 'albums' ? 'active' : ''}`}
            onClick={() => handleTabChange('albums')}
          >
            Альбомы
          </button>
          <button
            className={`tab ${activeTab === 'posts' ? 'active' : ''}`}
            onClick={() => handleTabChange('posts')}
          >
            Посты
          </button>
        </div>

        {/* Фильтры */}
        {renderFilters()}

        {/* Результаты */}
        <div className="search-results">
          {loading && query.trim() && (
            <div className="loading-results">
              <div className="spinner"></div>
              <span>Поиск...</span>
            </div>
          )}

          {!loading && renderResults()}
        </div>
      </div>
    </div>
  );
}

export default Search;