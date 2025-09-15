import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchCurrentUser();
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error de inicio de sesión' 
      };
    }
  };

  const register = async (email, password) => {
    try {
      await axios.post(`${API}/auth/register`, { email, password });
      return await login(email, password);
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error de registro' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Components
const Navbar = ({ currentPage, setCurrentPage }) => {
  const { user, logout } = useAuth();

  return (
    <nav className="cyber-nav">
      <div className="nav-container">
        <div className="nav-logo">
          <span className="logo-text">NeonSec</span>
          <span className="logo-subtitle">// Ethical Hacking Hub</span>
        </div>
        <div className="nav-links">
          <button 
            className={`nav-link ${currentPage === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentPage('home')}
          >
            <span className="terminal-prompt">~/</span> Inicio
          </button>
          {user && (
            <button 
              className={`nav-link ${currentPage === 'create' ? 'active' : ''}`}
              onClick={() => setCurrentPage('create')}
            >
              <span className="terminal-prompt">></span> Nueva Pregunta
            </button>
          )}
          <button 
            className={`nav-link ${currentPage === 'resources' ? 'active' : ''}`}
            onClick={() => setCurrentPage('resources')}
          >
            <span className="terminal-prompt">#</span> Recursos
          </button>
        </div>
        <div className="auth-section">
          {user ? (
            <div className="user-info">
              <span className="user-email">
                <span className="terminal-prompt">user@neonsec:</span> {user.email.split('@')[0]}
              </span>
              <button className="logout-btn" onClick={logout}>
                <span className="terminal-prompt">exit</span> Salir
              </button>
            </div>
          ) : (
            <div className="auth-buttons">
              <button 
                className={`nav-link ${currentPage === 'login' ? 'active' : ''}`}
                onClick={() => setCurrentPage('login')}
              >
                <span className="terminal-prompt">sudo</span> Login
              </button>
              <button 
                className={`nav-link ${currentPage === 'register' ? 'active' : ''}`}
                onClick={() => setCurrentPage('register')}
              >
                <span className="terminal-prompt">adduser</span> Registro
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

const LoginForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      onSuccess();
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2 className="auth-title">
          <span className="terminal-prompt">sudo</span> Iniciar Sesión
        </h2>
        
        {error && (
          <div className="error-message">
            <span className="terminal-prompt">error:</span> {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
              className="cyber-input"
              placeholder="tu@email.com"
            />
          </div>

          <div className="form-group">
            <label>Contraseña:</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
              className="cyber-input"
              placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={loading} className="auth-btn">
            <span className="terminal-prompt">./login</span>
            {loading ? ' Ingresando...' : ' Ingresar'}
          </button>
        </form>
      </div>
    </div>
  );
};

const RegisterForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({ email: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres');
      setLoading(false);
      return;
    }

    const result = await register(formData.email, formData.password);
    
    if (result.success) {
      onSuccess();
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2 className="auth-title">
          <span className="terminal-prompt">adduser</span> Crear Cuenta
        </h2>
        
        {error && (
          <div className="error-message">
            <span className="terminal-prompt">error:</span> {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email:</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
              className="cyber-input"
              placeholder="tu@email.com"
            />
          </div>

          <div className="form-group">
            <label>Contraseña:</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
              className="cyber-input"
              placeholder="••••••••"
            />
            <div className="password-hint">
              Mínimo 8 caracteres, incluye letras y números
            </div>
          </div>

          <div className="form-group">
            <label>Confirmar Contraseña:</label>
            <input
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
              required
              className="cyber-input"
              placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={loading} className="auth-btn">
            <span className="terminal-prompt">./register</span>
            {loading ? ' Creando cuenta...' : ' Crear Cuenta'}
          </button>
        </form>
      </div>
    </div>
  );
};

const TagList = ({ tags, selectedTag, onTagClick }) => {
  const popularTags = ['web', 'pentesting', 'osint', 'redteam', 'blueteam', 'malware', 'forensics', 'crypto', 'social-engineering', 'bug-bounty'];
  
  return (
    <div className="tag-filter">
      <h3 className="filter-title">
        <span className="terminal-prompt">cat</span> /tags
      </h3>
      <div className="tags-grid">
        <button 
          className={`tag ${!selectedTag ? 'active' : ''}`}
          onClick={() => onTagClick('')}
        >
          all
        </button>
        {popularTags.map(tag => (
          <button 
            key={tag}
            className={`tag ${selectedTag === tag ? 'active' : ''}`}
            onClick={() => onTagClick(tag)}
          >
            #{tag}
          </button>
        ))}
      </div>
    </div>
  );
};

const PostCard = ({ post, onClick }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="post-card" onClick={() => onClick(post)}>
      <div className="post-header">
        <h3 className="post-title">{post.title}</h3>
        <span className="post-date">{formatDate(post.created_at)}</span>
      </div>
      <p className="post-content">{post.content.substring(0, 200)}...</p>
      <div className="post-tags">
        {post.tags.map(tag => (
          <span key={tag} className="tag small">#{tag}</span>
        ))}
      </div>
      <div className="post-meta">
        <span className="author">
          <span className="terminal-prompt">user@neonsec:</span> {post.author}
        </span>
      </div>
    </div>
  );
};

const CreatePost = ({ onPostCreated, onCancel }) => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    tags: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const tagsArray = formData.tags.split(',').map(tag => tag.trim().toLowerCase()).filter(tag => tag);
      const postData = {
        title: formData.title,
        content: formData.content,
        tags: tagsArray
      };

      const response = await axios.post(`${API}/posts`, postData);
      onPostCreated(response.data);
      setFormData({ title: '', content: '', tags: '' });
    } catch (error) {
      console.error('Error creating post:', error);
      setError(error.response?.data?.detail || 'Error al crear el post');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="auth-required">
        <h2>
          <span className="terminal-prompt">access denied:</span> Login requerido
        </h2>
        <p>Necesitas iniciar sesión para crear posts.</p>
        <button className="cancel-btn" onClick={onCancel}>
          <span className="terminal-prompt">cd ..</span> Volver
        </button>
      </div>
    );
  }

  return (
    <div className="create-post">
      <div className="section-header">
        <h2>
          <span className="terminal-prompt">nano</span> nueva_pregunta.md
        </h2>
        <button className="cancel-btn" onClick={onCancel}>
          <span className="terminal-prompt">^X</span> Cancelar
        </button>
      </div>
      
      {error && (
        <div className="error-message">
          <span className="terminal-prompt">error:</span> {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="post-form">
        <div className="form-group">
          <label>Título:</label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({...formData, title: e.target.value})}
            required
            placeholder="¿Cuál es tu pregunta o recurso?"
            className="cyber-input"
          />
        </div>

        <div className="form-group">
          <label>Contenido:</label>
          <textarea
            value={formData.content}
            onChange={(e) => setFormData({...formData, content: e.target.value})}
            required
            rows="10"
            placeholder="Describe tu pregunta o comparte tu recurso..."
            className="cyber-textarea"
          />
        </div>

        <div className="form-group">
          <label>Tags (separados por comas):</label>
          <input
            type="text"
            value={formData.tags}
            onChange={(e) => setFormData({...formData, tags: e.target.value})}
            placeholder="web, pentesting, osint, redteam..."
            className="cyber-input"
          />
        </div>

        <button type="submit" disabled={isLoading} className="submit-btn">
          <span className="terminal-prompt">./publish</span> 
          {isLoading ? ' Publicando...' : ' Publicar'}
        </button>
      </form>
    </div>
  );
};

const PostDetail = ({ post, onBack }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState({ content: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    fetchComments();
  }, [post.id]);

  const fetchComments = async () => {
    try {
      const response = await axios.get(`${API}/comments/${post.id}`);
      setComments(response.data);
    } catch (error) {
      console.error('Error fetching comments:', error);
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!user) {
      setError('Necesitas iniciar sesión para comentar');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const commentData = {
        ...newComment,
        post_id: post.id
      };

      await axios.post(`${API}/comments`, commentData);
      setNewComment({ content: '' });
      fetchComments();
    } catch (error) {
      console.error('Error creating comment:', error);
      setError(error.response?.data?.detail || 'Error al crear el comentario');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="post-detail">
      <div className="section-header">
        <button className="back-btn" onClick={onBack}>
          <span className="terminal-prompt">cd ..</span> Volver
        </button>
      </div>

      <div className="post-full">
        <h1 className="post-title-full">{post.title}</h1>
        <div className="post-meta-full">
          <span className="author">
            <span className="terminal-prompt">user@neonsec:</span> {post.author}
          </span>
          <span className="date">{formatDate(post.created_at)}</span>
        </div>
        <div className="post-tags">
          {post.tags.map(tag => (
            <span key={tag} className="tag">#{tag}</span>
          ))}
        </div>
        <div className="post-content-full">
          {post.content.split('\n').map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
      </div>

      <div className="comments-section">
        <h3>
          <span className="terminal-prompt">ls</span> comentarios/ ({comments.length})
        </h3>
        
        {user ? (
          <form onSubmit={handleCommentSubmit} className="comment-form">
            {error && (
              <div className="error-message">
                <span className="terminal-prompt">error:</span> {error}
              </div>
            )}
            <div className="form-group">
              <textarea
                value={newComment.content}
                onChange={(e) => setNewComment({...newComment, content: e.target.value})}
                required
                rows="3"
                placeholder="Añade tu comentario..."
                className="cyber-textarea small"
              />
            </div>
            <div className="comment-form-footer">
              <span className="comment-author-info">
                Comentando como: <strong>{user.email.split('@')[0]}</strong>
              </span>
              <button type="submit" disabled={isLoading} className="comment-btn">
                <span className="terminal-prompt">></span> Comentar
              </button>
            </div>
          </form>
        ) : (
          <div className="auth-required-comment">
            <p><span className="terminal-prompt">!</span> Necesitas iniciar sesión para comentar</p>
          </div>
        )}

        <div className="comments-list">
          {comments.map(comment => (
            <div key={comment.id} className="comment">
              <div className="comment-header">
                <span className="comment-author">
                  <span className="terminal-prompt">></span> {comment.author}
                </span>
                <span className="comment-date">{formatDate(comment.created_at)}</span>
              </div>
              <p className="comment-content">{comment.content}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const HomePage = ({ posts, selectedTag, setSelectedTag, onPostClick }) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const filteredPosts = (posts || []).filter(post => {
    const matchesSearch = !searchTerm || 
      post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      post.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      post.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesTag = !selectedTag || post.tags.includes(selectedTag);
    
    return matchesSearch && matchesTag;
  });

  return (
    <div className="home-page">
      <div className="hero-section">
        <h1 className="hero-title">
          <span className="terminal-prompt">root@neonsec:</span> 
          <span className="typing-text"> Welcome to the Matrix_</span>
        </h1>
        <p className="hero-subtitle">
          Comunidad de hackers éticos • Preguntas • Recursos • Conocimiento compartido
        </p>
      </div>

      <div className="search-section">
        <div className="search-container">
          <span className="terminal-prompt">grep -i</span>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="buscar en posts..."
            className="search-input"
          />
        </div>
      </div>

      <TagList 
        selectedTag={selectedTag} 
        onTagClick={setSelectedTag}
      />

      <div className="posts-section">
        <div className="section-header">
          <h2>
            <span className="terminal-prompt">cat</span> recent_posts.log
            <span className="post-count">({filteredPosts.length})</span>
          </h2>
        </div>
        
        <div className="posts-grid">
          {filteredPosts.length === 0 ? (
            <div className="no-posts">
              <span className="terminal-prompt">404:</span> No se encontraron posts
            </div>
          ) : (
            filteredPosts.map(post => (
              <PostCard key={post.id} post={post} onClick={onPostClick} />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [selectedTag, setSelectedTag] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchPosts();
    // Add some sample data if no posts exist
    setTimeout(() => {
      createSamplePosts();
    }, 1000);
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await axios.get(`${API}/posts`);
      setPosts(response.data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createSamplePosts = async () => {
    try {
      const response = await axios.get(`${API}/posts`);
      if (response.data.length === 0) {
        // Sample posts will be created by backend testing or manually by users
        console.log('No posts found. Users can create posts after logging in.');
      }
    } catch (error) {
      console.error('Error checking posts:', error);
    }
  };

  const handlePostCreated = (newPost) => {
    setPosts([newPost, ...posts]);
    setCurrentPage('home');
  };

  const handlePostClick = (post) => {
    setSelectedPost(post);
    setCurrentPage('detail');
  };

  const handleAuthSuccess = () => {
    setCurrentPage('home');
    fetchPosts(); // Refresh posts after login
  };

  const renderPage = () => {
    if (isLoading) {
      return (
        <div className="loading">
          <span className="terminal-prompt">loading</span>
          <span className="loading-dots">...</span>
        </div>
      );
    }

    switch (currentPage) {
      case 'login':
        return <LoginForm onSuccess={handleAuthSuccess} />;
      case 'register':
        return <RegisterForm onSuccess={handleAuthSuccess} />;
      case 'create':
        return (
          <CreatePost 
            onPostCreated={handlePostCreated}
            onCancel={() => setCurrentPage('home')}
          />
        );
      case 'detail':
        return (
          <PostDetail 
            post={selectedPost}
            onBack={() => setCurrentPage('home')}
          />
        );
      case 'resources':
        return (
          <div className="resources-page">
            <h2><span className="terminal-prompt">ls</span> recursos/</h2>
            <p>Sección de recursos en desarrollo...</p>
          </div>
        );
      default:
        return (
          <HomePage 
            posts={posts}
            selectedTag={selectedTag}
            setSelectedTag={setSelectedTag}
            onPostClick={handlePostClick}
          />
        );
    }
  };

  return (
    <AuthProvider>
      <div className="App">
        <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />
        <main className="main-content">
          {renderPage()}
        </main>
      </div>
    </AuthProvider>
  );
}

export default App;
