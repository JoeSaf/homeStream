from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio

# Import models and utilities
from models import *
from auth import *
from database import get_database, create_indexes
from recommendation_engine import RecommendationEngine

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="Netflix Clone API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize recommendation engine
recommendation_engine = None

@app.on_event("startup")
async def startup_event():
    """Initialize the application."""
    global recommendation_engine
    db = await get_database()
    recommendation_engine = RecommendationEngine(db)
    await create_indexes()
    logging.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    from database import close_database
    await close_database()
    logging.info("Application shutdown")

# AUTHENTICATION ROUTES
@api_router.post("/auth/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Register a new user."""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        date_of_birth=user_data.date_of_birth,
        subscription_type=user_data.subscription_type,
        hashed_password=hashed_password
    )
    
    # Insert user
    await db.users.insert_one(user.dict())
    
    # Create default profile
    default_profile = Profile(
        user_id=user.id,
        name=f"{user_data.first_name}'s Profile",
        profile_type=ProfileType.ADULT
    )
    
    await db.profiles.insert_one(default_profile.dict())
    
    # Update user with profile ID
    await db.users.update_one(
        {"id": user.id},
        {"$push": {"profiles": default_profile.id}}
    )
    
    # Return user with profiles
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        subscription_type=user.subscription_type,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        profiles=[default_profile]
    )
    
    return user_response

@api_router.post("/auth/login", response_model=Token)
async def login_user(
    login_data: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Login user and return JWT token."""
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get current user information with profiles."""
    # Get user profiles
    profiles_data = await db.profiles.find({"user_id": current_user.id}).to_list(None)
    profiles = [Profile(**profile) for profile in profiles_data]
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        subscription_type=current_user.subscription_type,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        profiles=profiles
    )

# PROFILE ROUTES
@api_router.post("/profiles", response_model=Profile)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new profile."""
    if profile_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create profile for another user"
        )
    
    # Check profile limit (max 5 profiles per user)
    existing_profiles = await db.profiles.count_documents({"user_id": current_user.id})
    if existing_profiles >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 5 profiles allowed per account"
        )
    
    # Check if profile name already exists for this user
    existing_name = await db.profiles.find_one({
        "user_id": current_user.id,
        "name": profile_data.name
    })
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile name already exists"
        )
    
    profile = Profile(**profile_data.dict())
    await db.profiles.insert_one(profile.dict())
    
    # Update user with new profile ID
    await db.users.update_one(
        {"id": current_user.id},
        {"$push": {"profiles": profile.id}}
    )
    
    return profile

@api_router.get("/profiles", response_model=List[Profile])
async def get_user_profiles(
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all profiles for the current user."""
    profiles_data = await db.profiles.find({"user_id": current_user.id}).to_list(None)
    return [Profile(**profile) for profile in profiles_data]

@api_router.get("/profiles/{profile_id}", response_model=Profile)
async def get_profile(
    profile_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific profile."""
    profile_data = await db.profiles.find_one({
        "id": profile_id,
        "user_id": current_user.id
    })
    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return Profile(**profile_data)

@api_router.put("/profiles/{profile_id}", response_model=Profile)
async def update_profile(
    profile_id: str,
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update a profile."""
    # Check if profile belongs to current user
    existing_profile = await db.profiles.find_one({
        "id": profile_id,
        "user_id": current_user.id
    })
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update profile
    update_data = {k: v for k, v in profile_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.profiles.update_one(
        {"id": profile_id},
        {"$set": update_data}
    )
    
    # Return updated profile
    updated_profile = await db.profiles.find_one({"id": profile_id})
    return Profile(**updated_profile)

@api_router.delete("/profiles/{profile_id}")
async def delete_profile(
    profile_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a profile."""
    # Check if profile belongs to current user
    existing_profile = await db.profiles.find_one({
        "id": profile_id,
        "user_id": current_user.id
    })
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Don't allow deleting the last profile
    profile_count = await db.profiles.count_documents({"user_id": current_user.id})
    if profile_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last profile"
        )
    
    # Delete profile and related data
    await db.profiles.delete_one({"id": profile_id})
    await db.watch_history.delete_many({"profile_id": profile_id})
    await db.my_list.delete_many({"profile_id": profile_id})
    await db.reviews.delete_many({"profile_id": profile_id})
    await db.recommendations.delete_many({"profile_id": profile_id})
    
    # Remove from user's profile list
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"profiles": profile_id}}
    )
    
    return {"message": "Profile deleted successfully"}

# CONTENT ROUTES
@api_router.get("/content", response_model=List[ContentResponse])
async def get_content(
    content_type: Optional[ContentType] = None,
    genre_ids: Optional[List[int]] = Query(None),
    limit: int = 20,
    skip: int = 0,
    profile_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get content with optional filtering."""
    query = {}
    if content_type:
        query["content_type"] = content_type
    if genre_ids:
        query["genre_ids"] = {"$in": genre_ids}
    
    content_list = await db.content.find(query).skip(skip).limit(limit).to_list(None)
    
    # If profile_id provided, get user-specific data
    content_responses = []
    for content in content_list:
        content_response = ContentResponse(**content)
        
        if profile_id:
            # Check if in my list
            my_list_entry = await db.my_list.find_one({
                "profile_id": profile_id,
                "content_id": content["id"]
            })
            content_response.in_my_list = bool(my_list_entry)
            
            # Get user rating
            user_review = await db.reviews.find_one({
                "profile_id": profile_id,
                "content_id": content["id"]
            })
            if user_review:
                content_response.user_rating = user_review["rating"]
            
            # Get watch progress
            watch_history = await db.watch_history.find_one({
                "profile_id": profile_id,
                "content_id": content["id"]
            })
            if watch_history:
                content_response.watch_progress = watch_history["progress"]
        
        content_responses.append(content_response)
    
    return content_responses

@api_router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content_by_id(
    content_id: str,
    profile_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get specific content by ID."""
    content = await db.content.find_one({"id": content_id})
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    content_response = ContentResponse(**content)
    
    if profile_id:
        # Check if in my list
        my_list_entry = await db.my_list.find_one({
            "profile_id": profile_id,
            "content_id": content_id
        })
        content_response.in_my_list = bool(my_list_entry)
        
        # Get user rating
        user_review = await db.reviews.find_one({
            "profile_id": profile_id,
            "content_id": content_id
        })
        if user_review:
            content_response.user_rating = user_review["rating"]
        
        # Get watch progress
        watch_history = await db.watch_history.find_one({
            "profile_id": profile_id,
            "content_id": content_id
        })
        if watch_history:
            content_response.watch_progress = watch_history["progress"]
    
    return content_response

# WATCH HISTORY ROUTES
@api_router.post("/watch-history", response_model=WatchHistory)
async def update_watch_history(
    watch_data: WatchHistoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update watch history for a profile."""
    # Verify profile belongs to user
    profile = await db.profiles.find_one({
        "id": watch_data.profile_id,
        "user_id": current_user.id
    })
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile not found or access denied"
        )
    
    # Update or create watch history
    existing_history = await db.watch_history.find_one({
        "profile_id": watch_data.profile_id,
        "content_id": watch_data.content_id
    })
    
    if existing_history:
        # Update existing
        await db.watch_history.update_one(
            {"id": existing_history["id"]},
            {
                "$set": {
                    "progress": watch_data.progress,
                    "watch_time": watch_data.watch_time,
                    "status": watch_data.status,
                    "last_watched": datetime.utcnow()
                }
            }
        )
        updated_history = await db.watch_history.find_one({"id": existing_history["id"]})
        return WatchHistory(**updated_history)
    else:
        # Create new
        watch_history = WatchHistory(**watch_data.dict())
        await db.watch_history.insert_one(watch_history.dict())
        return watch_history

@api_router.get("/watch-history/{profile_id}", response_model=List[Dict[str, Any]])
async def get_watch_history(
    profile_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get watch history for a profile."""
    # Verify profile belongs to user
    profile = await db.profiles.find_one({
        "id": profile_id,
        "user_id": current_user.id
    })
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile not found or access denied"
        )
    
    # Get watch history with content details
    pipeline = [
        {"$match": {"profile_id": profile_id}},
        {"$sort": {"last_watched": -1}},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "content",
                "localField": "content_id",
                "foreignField": "id",
                "as": "content"
            }
        },
        {"$unwind": "$content"}
    ]
    
    watch_history = await db.watch_history.aggregate(pipeline).to_list(None)
    return watch_history

# MY LIST ROUTES
@api_router.post("/my-list")
async def add_to_my_list(
    my_list_data: MyListCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Add content to my list."""
    # Verify profile belongs to user
    profile = await db.profiles.find_one({
        "id": my_list_data.profile_id,
        "user_id": current_user.id
    })
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile not found or access denied"
        )
    
    # Check if already in list
    existing = await db.my_list.find_one({
        "profile_id": my_list_data.profile_id,
        "content_id": my_list_data.content_id
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content already in my list"
        )
    
    my_list_item = MyList(**my_list_data.dict())
    await db.my_list.insert_one(my_list_item.dict())
    
    return {"message": "Added to my list"}

@api_router.delete("/my-list/{profile_id}/{content_id}")
async def remove_from_my_list(
    profile_id: str,
    content_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Remove content from my list."""
    # Verify profile belongs to user
    profile = await db.profiles.find_one({
        "id": profile_id,
        "user_id": current_user.id
    })
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile not found or access denied"
        )
    
    result = await db.my_list.delete_one({
        "profile_id": profile_id,
        "content_id": content_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found in my list"
        )
    
    return {"message": "Removed from my list"}

@api_router.get("/my-list/{profile_id}", response_model=List[Dict[str, Any]])
async def get_my_list(
    profile_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get my list for a profile."""
    # Verify profile belongs to user
    profile = await db.profiles.find_one({
        "id": profile_id,
        "user_id": current_user.id
    })
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile not found or access denied"
        )
    
    # Get my list with content details
    pipeline = [
        {"$match": {"profile_id": profile_id}},
        {"$sort": {"added_at": -1}},
        {
            "$lookup": {
                "from": "content",
                "localField": "content_id",
                "foreignField": "id",
                "as": "content"
            }
        },
        {"$unwind": "$content"}
    ]
    
    my_list = await db.my_list.aggregate(pipeline).to_list(None)
    return my_list

# Basic route for testing
@api_router.get("/")
async def root():
    return {"message": "Netflix Clone API is running"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)