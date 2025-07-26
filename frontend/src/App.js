import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import './App.css';
import {
  Navbar,
  HeroBanner,
  ContentRow,
  VideoPlayer,
  SearchResults,
  useTMDB
} from './components';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [selectedItem, setSelectedItem] = useState(null);
  const [showSearch, setShowSearch] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [myList, setMyList] = useState([]);
  
  // Content state
  const [featuredContent, setFeaturedContent] = useState([]);
  const [trendingContent, setTrendingContent] = useState([]);
  const [popularMovies, setPopularMovies] = useState([]);
  const [popularTVShows, setPopularTVShows] = useState([]);
  const [topRatedMovies, setTopRatedMovies] = useState([]);
  const [upcomingMovies, setUpcomingMovies] = useState([]);
  const [nowPlayingMovies, setNowPlayingMovies] = useState([]);
  const [actionMovies, setActionMovies] = useState([]);
  const [comedyMovies, setComedyMovies] = useState([]);
  const [horrorMovies, setHorrorMovies] = useState([]);

  const tmdb = useTMDB();

  // Mock data in case API fails
  const mockContent = [
    {
      id: 1,
      title: "The Dark Knight",
      name: "The Dark Knight",
      overview: "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
      backdrop_path: null,
      genre_ids: [28, 80, 18]
    },
    {
      id: 2,
      title: "Inception",
      name: "Inception",
      overview: "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
      backdrop_path: null,
      genre_ids: [28, 878, 53]
    },
    {
      id: 3,
      title: "Pulp Fiction",
      name: "Pulp Fiction",
      overview: "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
      backdrop_path: null,
      genre_ids: [80, 18]
    },
    {
      id: 4,
      title: "The Godfather",
      name: "The Godfather",
      overview: "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
      backdrop_path: null,
      genre_ids: [80, 18]
    },
    {
      id: 5,
      title: "Breaking Bad",
      name: "Breaking Bad",
      overview: "A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family's future.",
      backdrop_path: null,
      genre_ids: [18, 80]
    },
    {
      id: 6,
      title: "Stranger Things",
      name: "Stranger Things",
      overview: "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces, and one strange little girl.",
      backdrop_path: null,
      genre_ids: [18, 14, 27]
    },
    {
      id: 7,
      title: "The Office",
      name: "The Office",
      overview: "A mockumentary on a group of typical office workers, where the workday consists of ego clashes, inappropriate behavior, and tedium.",
      backdrop_path: null,
      genre_ids: [35]
    },
    {
      id: 8,
      title: "Game of Thrones",
      name: "Game of Thrones",
      overview: "Nine noble families fight for control over the lands of Westeros, while an ancient enemy returns after being dormant for millennia.",
      backdrop_path: null,
      genre_ids: [18, 14, 10759]
    }
  ];

  // Load content on component mount
  useEffect(() => {
    loadContent();
  }, []);

  const loadContent = async () => {
    try {
      // Fetch different categories of content
      const [
        trending,
        popularMoviesData,
        popularTVData,
        topRatedData,
        upcomingData,
        nowPlayingData,
        actionData,
        comedyData,
        horrorData
      ] = await Promise.all([
        tmdb.getTrending(),
        tmdb.getPopular('movie'),
        tmdb.getPopular('tv'),
        tmdb.getTopRated('movie'),
        tmdb.getUpcoming(),
        tmdb.getNowPlaying(),
        tmdb.getGenreMovies(28), // Action
        tmdb.getGenreMovies(35), // Comedy
        tmdb.getGenreMovies(27)  // Horror
      ]);

      // Set content or use mock data if API fails
      setFeaturedContent((trending?.results || mockContent).slice(0, 5));
      setTrendingContent(trending?.results || mockContent);
      setPopularMovies(popularMoviesData?.results || mockContent);
      setPopularTVShows(popularTVData?.results || mockContent);
      setTopRatedMovies(topRatedData?.results || mockContent);
      setUpcomingMovies(upcomingData?.results || mockContent);
      setNowPlayingMovies(nowPlayingData?.results || mockContent);
      setActionMovies(actionData?.results || mockContent);
      setComedyMovies(comedyData?.results || mockContent);
      setHorrorMovies(horrorData?.results || mockContent);

    } catch (error) {
      console.error('Error loading content:', error);
      // Use mock data as fallback
      setFeaturedContent(mockContent.slice(0, 5));
      setTrendingContent(mockContent);
      setPopularMovies(mockContent);
      setPopularTVShows(mockContent);
      setTopRatedMovies(mockContent);
      setUpcomingMovies(mockContent);
      setNowPlayingMovies(mockContent);
      setActionMovies(mockContent);
      setComedyMovies(mockContent);
      setHorrorMovies(mockContent);
    }
  };

  const handleSearch = async (query) => {
    try {
      const results = await tmdb.searchMovies(query);
      setSearchResults(results?.results || []);
      setCurrentView('search');
    } catch (error) {
      console.error('Search error:', error);
      // Use filtered mock data for search
      const filtered = mockContent.filter(item => 
        (item.title || item.name).toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(filtered);
      setCurrentView('search');
    }
  };

  const handlePlayClick = (item) => {
    setSelectedItem(item);
    setCurrentView('player');
  };

  const handleAddToList = (item) => {
    if (!myList.find(listItem => listItem.id === item.id)) {
      setMyList([...myList, item]);
    }
  };

  const handleClosePlayer = () => {
    setSelectedItem(null);
    setCurrentView('home');
  };

  const handleCloseSearch = () => {
    setCurrentView('home');
    setSearchResults([]);
    setShowSearch(false);
  };

  return (
    <div className="bg-black min-h-screen">
      <Navbar 
        onSearch={handleSearch}
        showSearch={showSearch}
        setShowSearch={setShowSearch}
      />

      <AnimatePresence mode="wait">
        {currentView === 'home' && (
          <div key="home">
            <HeroBanner 
              featuredContent={featuredContent}
              onPlayClick={handlePlayClick}
            />
            
            <div className="relative -mt-32 z-10">
              <ContentRow
                title="Trending Now"
                items={trendingContent}
                onPlay={handlePlayClick}
                onAddToList={handleAddToList}
                isLarge={true}
              />
              
              <ContentRow
                title="Popular Movies"
                items={popularMovies}
                onPlay={handlePlayClick}
                onAddToList={handleAddToList}
              />
              
              <ContentRow
                title="Popular TV Shows"
                items={popularTVShows}
                onPlay={handlePlayClick}
                onAddToList={handleAddToList}
              />
              
              <ContentRow
                title="Top Rated Movies"
                items={topRatedMovies}
                onPlay={handlePlayClick}
                onAddToList={handleAddToList}
              />
              
              <ContentRow
                title="Now Playing"
                items={nowPlayingMovies}
                onPlay={handlePlayClick}
                onAddToList={handleAddToList}
              />
              
              <ContentRow
                title="Upcoming Movies"
                items={upcomingMovies}
                onPlay={handlePlayClick}
                onAddToList={handleAddToList}
              />
              
              <ContentRow
                title="Action Movies"
                items={actionMovies}
                onPlay={handlePlayClick}
                onAddToList={handleAddToList}
              />
              
              <ContentRow
                title="Comedy Movies"
                items={comedyMovies}
                onPlay={handlePlayClick}
                onAddToList={handleAddToList}
              />
              
              <ContentRow
                title="Horror Movies"
                items={horrorMovies}
                onPlay={handlePlayClick}
                onAddToList={handleAddToList}
              />
              
              {myList.length > 0 && (
                <ContentRow
                  title="My List"
                  items={myList}
                  onPlay={handlePlayClick}
                  onAddToList={handleAddToList}
                />
              )}
            </div>
          </div>
        )}

        {currentView === 'search' && (
          <SearchResults
            key="search"
            results={searchResults}
            onPlay={handlePlayClick}
            onAddToList={handleAddToList}
            onClose={handleCloseSearch}
          />
        )}

        {currentView === 'player' && selectedItem && (
          <VideoPlayer
            key="player"
            item={selectedItem}
            onClose={handleClosePlayer}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;