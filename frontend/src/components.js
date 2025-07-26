import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaPlay, 
  FaPlus, 
  FaChevronDown, 
  FaSearch, 
  FaBell, 
  FaUser,
  FaChevronLeft,
  FaChevronRight,
  FaTimes,
  FaThumbsUp,
  FaThumbsDown,
  FaVolumeMute,
  FaVolumeUp
} from 'react-icons/fa';
import axios from 'axios';

// TMDB API Configuration
const TMDB_API_KEYS = [
  'c8dea14dc917687ac631a52620e4f7ad',
  '3cb41ecea3bf606c56552db3d17adefd'
];
let currentApiKeyIndex = 0;

const getApiKey = () => TMDB_API_KEYS[currentApiKeyIndex];

const rotateApiKey = () => {
  currentApiKeyIndex = (currentApiKeyIndex + 1) % TMDB_API_KEYS.length;
};

// Netflix Navbar Component
export const Navbar = ({ onSearch, showSearch, setShowSearch }) => {
  const [scrolled, setScrolled] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery);
    }
  };

  return (
    <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
      scrolled ? 'bg-black' : 'bg-gradient-to-b from-black/70 to-transparent'
    }`}>
      <div className="px-4 sm:px-8 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <div className="text-red-600 text-3xl font-bold">NETFLIX</div>
          <div className="hidden md:flex space-x-6 text-white">
            <a href="#" className="hover:text-gray-300 transition-colors">Home</a>
            <a href="#" className="hover:text-gray-300 transition-colors">TV Shows</a>
            <a href="#" className="hover:text-gray-300 transition-colors">Movies</a>
            <a href="#" className="hover:text-gray-300 transition-colors">New & Popular</a>
            <a href="#" className="hover:text-gray-300 transition-colors">My List</a>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="relative">
            {showSearch ? (
              <form onSubmit={handleSearch} className="flex items-center">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search movies, shows..."
                  className="bg-black/80 border border-white/30 text-white px-4 py-2 rounded-md w-64 focus:outline-none focus:border-white"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={() => setShowSearch(false)}
                  className="text-white ml-2 hover:text-gray-300"
                >
                  <FaTimes />
                </button>
              </form>
            ) : (
              <button
                onClick={() => setShowSearch(true)}
                className="text-white hover:text-gray-300 transition-colors"
              >
                <FaSearch size={20} />
              </button>
            )}
          </div>
          <FaBell className="text-white cursor-pointer hover:text-gray-300 transition-colors" size={20} />
          <div className="flex items-center space-x-2 cursor-pointer group">
            <FaUser className="text-white group-hover:text-gray-300 transition-colors" size={20} />
            <FaChevronDown className="text-white group-hover:text-gray-300 transition-colors" size={12} />
          </div>
        </div>
      </div>
    </nav>
  );
};

// Hero Banner Component
export const HeroBanner = ({ featuredContent, onPlayClick }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % featuredContent.length);
    }, 8000);
    return () => clearInterval(interval);
  }, [featuredContent.length]);

  if (!featuredContent.length) return null;

  const current = featuredContent[currentIndex];

  return (
    <div className="relative h-screen overflow-hidden">
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1 }}
          className="absolute inset-0"
        >
          <div 
            className="w-full h-full bg-cover bg-center bg-no-repeat"
            style={{
              backgroundImage: `url(https://images.unsplash.com/photo-1499364615650-ec38552f4f34?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxlbnRlcnRhaW5tZW50fGVufDB8fHx8MTc1MzUxNjIwNXww&ixlib=rb-4.1.0&q=85)`
            }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/40 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
          </div>
        </motion.div>
      </AnimatePresence>

      <div className="absolute inset-0 flex items-center">
        <div className="px-4 sm:px-8 max-w-2xl">
          <motion.h1 
            className="text-4xl sm:text-6xl font-bold text-white mb-4 leading-tight"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            {current.title || current.name}
          </motion.h1>
          
          <motion.p 
            className="text-lg sm:text-xl text-white/90 mb-8 line-clamp-3"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            {current.overview}
          </motion.p>
          
          <motion.div 
            className="flex space-x-4"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
          >
            <button 
              onClick={() => onPlayClick(current)}
              className="bg-white text-black px-8 py-3 rounded-md font-semibold flex items-center space-x-2 hover:bg-white/80 transition-all transform hover:scale-105"
            >
              <FaPlay /> <span>Play</span>
            </button>
            <button className="bg-gray-600/70 text-white px-8 py-3 rounded-md font-semibold flex items-center space-x-2 hover:bg-gray-600/50 transition-all">
              <FaPlus /> <span>My List</span>
            </button>
          </motion.div>
        </div>
      </div>
      
      {/* Navigation dots */}
      <div className="absolute bottom-8 right-8 flex space-x-2">
        {featuredContent.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentIndex(index)}
            className={`w-3 h-3 rounded-full transition-all ${
              index === currentIndex ? 'bg-white' : 'bg-white/40 hover:bg-white/60'
            }`}
          />
        ))}
      </div>
    </div>
  );
};

// Movie/Show Card Component
export const MovieCard = ({ item, onPlay, onAddToList, isLarge = false }) => {
  const [isHovered, setIsHovered] = useState(false);

  const cardImages = [
    'https://images.unsplash.com/photo-1577490621716-b1aa5f091524?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwxfHxjaW5lbWF8ZW58MHx8fHJlZHwxNzUzNTU0NzgxfDA&ixlib=rb-4.1.0&q=85',
    'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwyfHxmaWxtfGVufDB8fHx8MTc1MzU1NDc4OHww&ixlib=rb-4.1.0&q=85',
    'https://images.unsplash.com/photo-1551664723-61788d761795?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHw0fHxjaW5lbWF8ZW58MHx8fHJlZHwxNzUzNTU0NzgxfDA&ixlib=rb-4.1.0&q=85',
    'https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHxmaWxtfGVufDB8fHx8MTc1MzU1NDc4OHww&ixlib=rb-4.1.0&q=85',
    'https://images.unsplash.com/photo-1485846234645-a62644f84728?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwzfHxmaWxtfGVufDB8fHx8MTc1MzU1NDc4OHww&ixlib=rb-4.1.0&q=85',
    'https://images.unsplash.com/photo-1478720568477-152d9b164e26?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHw0fHxmaWxtfGVufDB8fHx8MTc1MzU1NDc4OHww&ixlib=rb-4.1.0&q=85',
    'https://images.unsplash.com/photo-1560169897-fc0cdbdfa4d5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHwxfHxzdHJlYW1pbmd8ZW58MHx8fHwxNzUzNDU0MjQ1fDA&ixlib=rb-4.1.0&q=85',
    'https://images.unsplash.com/photo-1646861039459-fd9e3aabf3fb?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzZ8MHwxfHNlYXJjaHwyfHxzdHJlYW1pbmd8ZW58MHx8fHwxNzUzNDU0MjQ1fDA&ixlib=rb-4.1.0&q=85'
  ];

  const randomImage = cardImages[Math.floor(Math.random() * cardImages.length)];

  return (
    <motion.div
      className={`relative cursor-pointer group ${isLarge ? 'h-80' : 'h-40'} flex-shrink-0`}
      style={{ width: isLarge ? '320px' : '240px' }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ scale: 1.05, zIndex: 10 }}
      transition={{ duration: 0.3 }}
    >
      <div
        className="w-full h-full bg-cover bg-center rounded-md overflow-hidden"
        style={{
          backgroundImage: `url(${item.backdrop_path ? `https://image.tmdb.org/t/p/w500${item.backdrop_path}` : randomImage})`
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        <AnimatePresence>
          {isHovered && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="absolute bottom-4 left-4 right-4"
            >
              <h3 className="text-white font-semibold text-sm mb-2 line-clamp-2">
                {item.title || item.name}
              </h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onPlay(item)}
                  className="bg-white text-black p-2 rounded-full hover:bg-white/80 transition-colors"
                >
                  <FaPlay size={12} />
                </button>
                <button
                  onClick={() => onAddToList(item)}
                  className="bg-gray-600/70 text-white p-2 rounded-full hover:bg-gray-600/50 transition-colors"
                >
                  <FaPlus size={12} />
                </button>
                <button className="bg-gray-600/70 text-white p-2 rounded-full hover:bg-gray-600/50 transition-colors">
                  <FaThumbsUp size={12} />
                </button>
                <button className="bg-gray-600/70 text-white p-2 rounded-full hover:bg-gray-600/50 transition-colors">
                  <FaChevronDown size={12} />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

// Content Row Component
export const ContentRow = ({ title, items, onPlay, onAddToList, isLarge = false }) => {
  const [scrollPosition, setScrollPosition] = useState(0);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const scrollLeft = () => {
    const container = document.getElementById(`row-${title.replace(/\s+/g, '-')}`);
    const newPosition = Math.max(0, scrollPosition - 960);
    container.scrollTo({ left: newPosition, behavior: 'smooth' });
    setScrollPosition(newPosition);
  };

  const scrollRight = () => {
    const container = document.getElementById(`row-${title.replace(/\s+/g, '-')}`);
    const newPosition = scrollPosition + 960;
    container.scrollTo({ left: newPosition, behavior: 'smooth' });
    setScrollPosition(newPosition);
  };

  useEffect(() => {
    const container = document.getElementById(`row-${title.replace(/\s+/g, '-')}`);
    if (container) {
      setCanScrollLeft(scrollPosition > 0);
      setCanScrollRight(scrollPosition < container.scrollWidth - container.clientWidth);
    }
  }, [scrollPosition, title]);

  return (
    <div className="mb-8 group">
      <h2 className="text-white text-xl font-semibold mb-4 px-4 sm:px-8">{title}</h2>
      <div className="relative">
        {canScrollLeft && (
          <button
            onClick={scrollLeft}
            className="absolute left-2 top-1/2 transform -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/70"
          >
            <FaChevronLeft />
          </button>
        )}
        
        <div
          id={`row-${title.replace(/\s+/g, '-')}`}
          className="flex space-x-4 overflow-x-hidden px-4 sm:px-8 scroll-smooth"
        >
          {items.map((item, index) => (
            <MovieCard
              key={item.id || index}
              item={item}
              onPlay={onPlay}
              onAddToList={onAddToList}
              isLarge={isLarge}
            />
          ))}
        </div>
        
        {canScrollRight && (
          <button
            onClick={scrollRight}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 z-10 bg-black/50 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/70"
          >
            <FaChevronRight />
          </button>
        )}
      </div>
    </div>
  );
};

// Video Player Component
export const VideoPlayer = ({ item, onClose }) => {
  const [isMuted, setIsMuted] = useState(true);
  const [showControls, setShowControls] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setShowControls(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  // Mock YouTube video ID (in real implementation, you'd get this from TMDB videos endpoint)
  const getYouTubeVideoId = () => {
    const videoIds = [
      'dQw4w9WgXcQ', // Rick Astley - Never Gonna Give You Up
      'L_jWHffIx5E', // Smash Mouth - All Star
      'ZbZSe6N_BXs', // Happy by Pharrell Williams
      'kffacxfA7G4', // Baby Shark
      '60ItHr2R7ZY', // Alan Walker - Faded
    ];
    return videoIds[Math.floor(Math.random() * videoIds.length)];
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black z-50 flex items-center justify-center"
      onMouseMove={() => setShowControls(true)}
    >
      <div className="relative w-full h-full">
        <iframe
          src={`https://www.youtube.com/embed/${getYouTubeVideoId()}?autoplay=1&mute=${isMuted ? 1 : 0}&controls=0&rel=0`}
          className="w-full h-full"
          allow="autoplay; encrypted-media"
          allowFullScreen
        />
        
        <AnimatePresence>
          {showControls && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/60"
            >
              {/* Top Controls */}
              <div className="absolute top-4 left-4 right-4 flex justify-between items-center">
                <h1 className="text-white text-2xl font-bold">{item.title || item.name}</h1>
                <button
                  onClick={onClose}
                  className="text-white p-2 hover:bg-white/20 rounded-full transition-colors"
                >
                  <FaTimes size={24} />
                </button>
              </div>
              
              {/* Bottom Controls */}
              <div className="absolute bottom-4 left-4 right-4 flex items-center space-x-4">
                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className="text-white p-2 hover:bg-white/20 rounded-full transition-colors"
                >
                  {isMuted ? <FaVolumeMute size={20} /> : <FaVolumeUp size={20} />}
                </button>
                <div className="flex-1 bg-white/30 h-1 rounded-full">
                  <div className="bg-red-600 h-1 rounded-full w-1/3"></div>
                </div>
                <span className="text-white text-sm">1:23 / 4:56</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

// Search Results Component
export const SearchResults = ({ results, onPlay, onAddToList, onClose }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      className="bg-black/95 min-h-screen pt-20"
    >
      <div className="px-4 sm:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-white text-3xl font-bold">Search Results</h1>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-300 transition-colors"
          >
            <FaTimes size={24} />
          </button>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {results.map((item) => (
            <MovieCard
              key={item.id}
              item={item}
              onPlay={onPlay}
              onAddToList={onAddToList}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
};

// Custom Hook for TMDB API
export const useTMDB = () => {
  const [loading, setLoading] = useState(false);

  const fetchData = async (endpoint) => {
    setLoading(true);
    try {
      const response = await axios.get(
        `https://api.themoviedb.org/3${endpoint}?api_key=${getApiKey()}&language=en-US`
      );
      return response.data;
    } catch (error) {
      if (error.response?.status === 429) {
        rotateApiKey();
        // Retry with new API key
        try {
          const response = await axios.get(
            `https://api.themoviedb.org/3${endpoint}?api_key=${getApiKey()}&language=en-US`
          );
          return response.data;
        } catch (retryError) {
          console.error('TMDB API Error after retry:', retryError);
          return null;
        }
      }
      console.error('TMDB API Error:', error);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const searchMovies = async (query) => {
    return await fetchData(`/search/multi?query=${encodeURIComponent(query)}`);
  };

  const getPopular = async (type = 'movie') => {
    return await fetchData(`/${type}/popular`);
  };

  const getTrending = async (mediaType = 'all', timeWindow = 'week') => {
    return await fetchData(`/trending/${mediaType}/${timeWindow}`);
  };

  const getTopRated = async (type = 'movie') => {
    return await fetchData(`/${type}/top_rated`);
  };

  const getUpcoming = async () => {
    return await fetchData('/movie/upcoming');
  };

  const getNowPlaying = async () => {
    return await fetchData('/movie/now_playing');
  };

  const getGenreMovies = async (genreId) => {
    return await fetchData(`/discover/movie?with_genres=${genreId}`);
  };

  return {
    loading,
    searchMovies,
    getPopular,
    getTrending,
    getTopRated,
    getUpcoming,
    getNowPlaying,
    getGenreMovies,
  };
};