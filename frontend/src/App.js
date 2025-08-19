import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Components
const Navbar = ({ currentPage, setCurrentPage }) => {
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
          <button 
            className={`nav-link ${currentPage === 'create' ? 'active' : ''}`}
            onClick={() => setCurrentPage('create')}
          >
            <span className="terminal-prompt">></span> Nueva Pregunta
          </button>
          <button 
            className={`nav-link ${currentPage === 'resources' ? 'active' : ''}`}
            onClick={() => setCurrentPage('resources')}
          >
            <span className="terminal-prompt">#</span> Recursos
          </button>
        </div>
      </div>
    </nav>
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
    tags: '',
    author: 'Anonymous'
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const tagsArray = formData.tags.split(',').map(tag => tag.trim().toLowerCase()).filter(tag => tag);
      const postData = {
        ...formData,
        tags: tagsArray
      };

      const response = await axios.post(`${API}/posts`, postData);
      onPostCreated(response.data);
      setFormData({ title: '', content: '', tags: '', author: 'Anonymous' });
    } catch (error) {
      console.error('Error creating post:', error);
    } finally {
      setIsLoading(false);
    }
  };

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

        <div className="form-group">
          <label>Autor:</label>
          <input
            type="text"
            value={formData.author}
            onChange={(e) => setFormData({...formData, author: e.target.value})}
            placeholder="Tu nombre o handle"
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
  const [newComment, setNewComment] = useState({ content: '', author: 'Anonymous' });
  const [isLoading, setIsLoading] = useState(false);

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
    setIsLoading(true);

    try {
      const commentData = {
        ...newComment,
        post_id: post.id
      };

      await axios.post(`${API}/comments`, commentData);
      setNewComment({ content: '', author: 'Anonymous' });
      fetchComments();
    } catch (error) {
      console.error('Error creating comment:', error);
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
        
        <form onSubmit={handleCommentSubmit} className="comment-form">
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
            <input
              type="text"
              value={newComment.author}
              onChange={(e) => setNewComment({...newComment, author: e.target.value})}
              placeholder="Tu nombre"
              className="cyber-input small"
            />
            <button type="submit" disabled={isLoading} className="comment-btn">
              <span className="terminal-prompt">></span> Comentar
            </button>
          </div>
        </form>

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
  
  const filteredPosts = posts.filter(post => {
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
        const samplePosts = [
          {
            title: "¿Mejores herramientas para OSINT en 2024?",
            content: "¡Hola hackers! Estoy empezando en OSINT y me gustaría conocer las mejores herramientas actuales. He estado usando Maltego y Shodan, pero quiero expandir mi toolkit. ¿Qué recomiendan para:\n\n- Búsqueda de información en redes sociales\n- Análisis de dominios y subdominios\n- Reconocimiento de infraestructura\n\n¿Alguna herramienta nueva que valga la pena?",
            tags: ["osint", "herramientas", "reconocimiento"],
            author: "n00b_investigator"
          },
          {
            title: "Bypass de WAF con técnicas avanzadas de evasión",
            content: "Comparto algunas técnicas que he estado probando para evadir WAFs modernos:\n\n1. **Encoding múltiple**: Combinar URL encoding con Unicode\n2. **HTTP Parameter Pollution**: Duplicar parámetros\n3. **Case variation**: Alternar mayúsculas/minúsculas\n\nEjemplo práctico:\n```\n' UNION/**/SELECT/**/1,2,3--\n' %55NION %53ELECT 1,2,3--\n```\n\n¿Alguien ha probado técnicas similares? ¿Qué WAFs son más resistentes?",
            tags: ["web", "pentesting", "waf", "bypass"],
            author: "sql_ninja"
          },
          {
            title: "Red Team vs Blue Team: Ejercicio práctico de defensa",
            content: "Organizamos un ejercicio de Red Team vs Blue Team en nuestro lab. Algunos hallazgos interesantes:\n\n**Red Team logró:**\n- Phishing exitoso (70% tasa de éxito)\n- Escalación de privilegios via kernel exploit\n- Persistencia con scheduled tasks\n\n**Blue Team detectó:**\n- Anomalías en logs de PowerShell\n- Conexiones sospechosas con C2\n- Modificaciones en registry\n\n¿Qué técnicas de detección recomiendan para mejorar la defensa?",
            tags: ["redteam", "blueteam", "ejercicio", "deteccion"],
            author: "cyber_defender"
          }
        ];

        for (const post of samplePosts) {
          await axios.post(`${API}/posts`, post);
        }
        
        fetchPosts();
      }
    } catch (error) {
      console.error('Error creating sample posts:', error);
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
    <div className="App">
      <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;