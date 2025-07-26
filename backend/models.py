from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class ProfileType(str, Enum):
    ADULT = "adult"
    KIDS = "kids"
    TEEN = "teen"

class ContentType(str, Enum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    DOCUMENTARY = "documentary"

class WatchStatus(str, Enum):
    WATCHING = "watching"
    COMPLETED = "completed"
    PLAN_TO_WATCH = "plan_to_watch"
    DROPPED = "dropped"

# User Models
class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    subscription_type: str = "basic"  # basic, standard, premium
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    subscription_type: Optional[str] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    subscription_type: str = "basic"
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    hashed_password: str
    profiles: List[str] = []  # Profile IDs

# Profile Models
class ProfileBase(BaseModel):
    name: str
    avatar_url: Optional[str] = None
    profile_type: ProfileType = ProfileType.ADULT
    language: str = "en"
    maturity_rating: str = "18+"  # G, PG, PG-13, R, 18+
    auto_play_next: bool = True
    auto_play_previews: bool = True

class ProfileCreate(ProfileBase):
    user_id: str

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    language: Optional[str] = None
    maturity_rating: Optional[str] = None
    auto_play_next: Optional[bool] = None
    auto_play_previews: Optional[bool] = None

class Profile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    avatar_url: Optional[str] = None
    profile_type: ProfileType = ProfileType.ADULT
    language: str = "en"
    maturity_rating: str = "18+"
    auto_play_next: bool = True
    auto_play_previews: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Content Models
class ContentBase(BaseModel):
    tmdb_id: int
    title: str
    original_title: Optional[str] = None
    overview: str
    content_type: ContentType
    genre_ids: List[int] = []
    release_date: Optional[datetime] = None
    runtime: Optional[int] = None  # in minutes
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    trailer_url: Optional[str] = None
    imdb_rating: Optional[float] = None
    tmdb_rating: Optional[float] = None
    language: str = "en"
    country: Optional[str] = None
    director: Optional[str] = None
    cast: List[str] = []
    production_companies: List[str] = []

class Content(ContentBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    average_rating: float = 0.0
    total_ratings: int = 0
    total_reviews: int = 0

# Watch History Models
class WatchHistoryBase(BaseModel):
    content_id: str
    profile_id: str
    progress: float = 0.0  # Percentage watched (0-100)
    watch_time: int = 0  # Total watch time in seconds
    status: WatchStatus = WatchStatus.WATCHING

class WatchHistoryCreate(WatchHistoryBase):
    pass

class WatchHistoryUpdate(BaseModel):
    progress: Optional[float] = None
    watch_time: Optional[int] = None
    status: Optional[WatchStatus] = None

class WatchHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    profile_id: str
    progress: float = 0.0
    watch_time: int = 0
    status: WatchStatus = WatchStatus.WATCHING
    last_watched: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# My List Models
class MyListBase(BaseModel):
    content_id: str
    profile_id: str

class MyListCreate(MyListBase):
    pass

class MyList(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    profile_id: str
    added_at: datetime = Field(default_factory=datetime.utcnow)

# Review Models
class ReviewBase(BaseModel):
    content_id: str
    profile_id: str
    rating: float = Field(..., ge=0.5, le=5.0)  # 0.5 to 5.0 stars
    review_text: Optional[str] = None
    is_spoiler: bool = False

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=0.5, le=5.0)
    review_text: Optional[str] = None
    is_spoiler: Optional[bool] = None

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    profile_id: str
    profile_name: str  # Denormalized for easier display
    rating: float
    review_text: Optional[str] = None
    is_spoiler: bool = False
    likes: int = 0
    dislikes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Review Reaction Models
class ReviewReactionBase(BaseModel):
    review_id: str
    profile_id: str
    reaction_type: str  # "like" or "dislike"

class ReviewReactionCreate(ReviewReactionBase):
    pass

class ReviewReaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    review_id: str
    profile_id: str
    reaction_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Recommendation Models
class RecommendationBase(BaseModel):
    profile_id: str
    content_id: str
    score: float  # Recommendation confidence score (0-1)
    reason: str  # Why this was recommended
    algorithm_used: str  # collaborative, content-based, hybrid, trending

class Recommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str
    content_id: str
    score: float
    reason: str
    algorithm_used: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    clicked: bool = False
    clicked_at: Optional[datetime] = None

# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Response Models
class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    subscription_type: str
    role: str
    is_active: bool
    created_at: datetime
    profiles: List[Profile] = []

class ContentResponse(BaseModel):
    id: str
    tmdb_id: int
    title: str
    overview: str
    content_type: str
    genre_ids: List[int]
    release_date: Optional[datetime]
    poster_path: Optional[str]
    backdrop_path: Optional[str]
    trailer_url: Optional[str]
    average_rating: float
    total_ratings: int
    total_reviews: int
    user_rating: Optional[float] = None
    in_my_list: bool = False
    watch_progress: Optional[float] = None

class ReviewResponse(BaseModel):
    id: str
    profile_name: str
    rating: float
    review_text: Optional[str]
    is_spoiler: bool
    likes: int
    dislikes: int
    created_at: datetime
    user_reaction: Optional[str] = None  # User's reaction to this review

# Analytics Models
class ViewingStats(BaseModel):
    total_watch_time: int  # in minutes
    content_watched: int
    favorite_genres: List[Dict[str, Any]]
    most_watched_day: str
    avg_session_time: int  # in minutes

class GenrePreference(BaseModel):
    genre_id: int
    genre_name: str
    watch_count: int
    total_time: int  # in minutes
    preference_score: float