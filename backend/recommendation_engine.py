from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
import asyncio
from .models import Recommendation, Content, Profile, WatchHistory, Review

class RecommendationEngine:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.content_features = None
        self.content_similarity_matrix = None
        self.user_item_matrix = None
        self.svd_model = None
        
    async def get_user_profiles_data(self, profile_id: str) -> Dict[str, Any]:
        """Get user profile data for recommendations."""
        # Get watch history
        watch_history = await self.db.watch_history.find(
            {"profile_id": profile_id}
        ).to_list(None)
        
        # Get ratings/reviews
        reviews = await self.db.reviews.find(
            {"profile_id": profile_id}
        ).to_list(None)
        
        # Get my list
        my_list = await self.db.my_list.find(
            {"profile_id": profile_id}
        ).to_list(None)
        
        return {
            "watch_history": watch_history,
            "reviews": reviews,
            "my_list": my_list
        }
    
    async def get_content_based_recommendations(
        self, 
        profile_id: str, 
        limit: int = 20
    ) -> List[str]:
        """Get content-based recommendations."""
        user_data = await self.get_user_profiles_data(profile_id)
        
        # Get user's watched content
        watched_content_ids = [item["content_id"] for item in user_data["watch_history"]]
        rated_content_ids = [item["content_id"] for item in user_data["reviews"]]
        
        # Combine watched and rated content
        user_content_ids = list(set(watched_content_ids + rated_content_ids))
        
        if not user_content_ids:
            return await self.get_trending_recommendations(limit)
        
        # Get content details
        user_content = await self.db.content.find(
            {"id": {"$in": user_content_ids}}
        ).to_list(None)
        
        if not user_content:
            return await self.get_trending_recommendations(limit)
        
        # Extract user preferences
        user_genres = []
        user_directors = []
        user_cast = []
        
        for content in user_content:
            user_genres.extend(content.get("genre_ids", []))
            if content.get("director"):
                user_directors.append(content["director"])
            user_cast.extend(content.get("cast", []))
        
        # Get genre preferences (most common genres)
        genre_counts = {}
        for genre in user_genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        preferred_genre_ids = [genre[0] for genre in top_genres]
        
        # Find similar content
        recommendations = await self.db.content.find({
            "id": {"$nin": user_content_ids},
            "genre_ids": {"$in": preferred_genre_ids}
        }).sort("average_rating", -1).limit(limit).to_list(None)
        
        return [rec["id"] for rec in recommendations]
    
    async def get_collaborative_recommendations(
        self, 
        profile_id: str, 
        limit: int = 20
    ) -> List[str]:
        """Get collaborative filtering recommendations."""
        # Get users with similar taste
        user_data = await self.get_user_profiles_data(profile_id)
        user_ratings = {item["content_id"]: item["rating"] for item in user_data["reviews"]}
        
        if not user_ratings:
            return await self.get_trending_recommendations(limit)
        
        # Get all users' ratings
        all_reviews = await self.db.reviews.find().to_list(None)
        
        # Build user-item matrix
        user_profiles = {}
        for review in all_reviews:
            pid = review["profile_id"]
            if pid not in user_profiles:
                user_profiles[pid] = {}
            user_profiles[pid][review["content_id"]] = review["rating"]
        
        # Find similar users
        similar_users = []
        for other_profile_id, other_ratings in user_profiles.items():
            if other_profile_id == profile_id:
                continue
            
            # Calculate similarity (Pearson correlation)
            common_items = set(user_ratings.keys()) & set(other_ratings.keys())
            if len(common_items) < 2:
                continue
            
            sum1 = sum([user_ratings[item] for item in common_items])
            sum2 = sum([other_ratings[item] for item in common_items])
            
            sum1_sq = sum([user_ratings[item] ** 2 for item in common_items])
            sum2_sq = sum([other_ratings[item] ** 2 for item in common_items])
            
            sum_products = sum([user_ratings[item] * other_ratings[item] for item in common_items])
            
            n = len(common_items)
            numerator = sum_products - (sum1 * sum2 / n)
            denominator = ((sum1_sq - sum1 ** 2 / n) * (sum2_sq - sum2 ** 2 / n)) ** 0.5
            
            if denominator == 0:
                correlation = 0
            else:
                correlation = numerator / denominator
            
            if correlation > 0.3:  # Threshold for similarity
                similar_users.append((other_profile_id, correlation))
        
        # Sort by similarity
        similar_users.sort(key=lambda x: x[1], reverse=True)
        
        # Get recommendations from similar users
        recommendations = {}
        for similar_user_id, similarity in similar_users[:10]:  # Top 10 similar users
            similar_user_ratings = user_profiles[similar_user_id]
            for content_id, rating in similar_user_ratings.items():
                if content_id not in user_ratings and rating >= 4.0:  # High rating
                    if content_id not in recommendations:
                        recommendations[content_id] = 0
                    recommendations[content_id] += rating * similarity
        
        # Sort recommendations by score
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [rec[0] for rec in sorted_recommendations[:limit]]
    
    async def get_trending_recommendations(self, limit: int = 20) -> List[str]:
        """Get trending content recommendations."""
        # Get content with high ratings and recent activity
        trending = await self.db.content.aggregate([
            {
                "$match": {
                    "total_ratings": {"$gte": 5},
                    "average_rating": {"$gte": 3.5}
                }
            },
            {
                "$sort": {
                    "total_ratings": -1,
                    "average_rating": -1
                }
            },
            {"$limit": limit}
        ]).to_list(None)
        
        return [item["id"] for item in trending]
    
    async def get_genre_based_recommendations(
        self, 
        profile_id: str, 
        genre_ids: List[int], 
        limit: int = 20
    ) -> List[str]:
        """Get recommendations based on specific genres."""
        user_data = await self.get_user_profiles_data(profile_id)
        watched_content_ids = [item["content_id"] for item in user_data["watch_history"]]
        
        recommendations = await self.db.content.find({
            "id": {"$nin": watched_content_ids},
            "genre_ids": {"$in": genre_ids}
        }).sort("average_rating", -1).limit(limit).to_list(None)
        
        return [rec["id"] for rec in recommendations]
    
    async def get_continue_watching_recommendations(
        self, 
        profile_id: str, 
        limit: int = 10
    ) -> List[str]:
        """Get continue watching recommendations."""
        continue_watching = await self.db.watch_history.find({
            "profile_id": profile_id,
            "progress": {"$gt": 5, "$lt": 90},  # Between 5% and 90%
            "status": "watching"
        }).sort("last_watched", -1).limit(limit).to_list(None)
        
        return [item["content_id"] for item in continue_watching]
    
    async def generate_recommendations(self, profile_id: str) -> Dict[str, Any]:
        """Generate comprehensive recommendations for a profile."""
        # Get different types of recommendations
        content_based = await self.get_content_based_recommendations(profile_id, 15)
        collaborative = await self.get_collaborative_recommendations(profile_id, 15)
        trending = await self.get_trending_recommendations(10)
        continue_watching = await self.get_continue_watching_recommendations(profile_id, 10)
        
        # Get user's genre preferences for genre-specific recommendations
        user_data = await self.get_user_profiles_data(profile_id)
        user_genres = []
        for item in user_data["watch_history"]:
            content = await self.db.content.find_one({"id": item["content_id"]})
            if content:
                user_genres.extend(content.get("genre_ids", []))
        
        # Get most common genres
        genre_counts = {}
        for genre in user_genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        genre_recommendations = {}
        for genre_id, _ in top_genres:
            genre_recs = await self.get_genre_based_recommendations(profile_id, [genre_id], 10)
            genre_recommendations[f"genre_{genre_id}"] = genre_recs
        
        # Store recommendations in database
        recommendation_data = []
        
        # Content-based recommendations
        for i, content_id in enumerate(content_based):
            recommendation_data.append(Recommendation(
                profile_id=profile_id,
                content_id=content_id,
                score=0.9 - (i * 0.05),  # Decreasing score
                reason="Based on your viewing history",
                algorithm_used="content_based"
            ).dict())
        
        # Collaborative recommendations
        for i, content_id in enumerate(collaborative):
            recommendation_data.append(Recommendation(
                profile_id=profile_id,
                content_id=content_id,
                score=0.85 - (i * 0.04),
                reason="Users with similar taste also liked",
                algorithm_used="collaborative"
            ).dict())
        
        # Trending recommendations
        for i, content_id in enumerate(trending):
            recommendation_data.append(Recommendation(
                profile_id=profile_id,
                content_id=content_id,
                score=0.8 - (i * 0.03),
                reason="Trending now",
                algorithm_used="trending"
            ).dict())
        
        # Clear old recommendations for this profile
        await self.db.recommendations.delete_many({"profile_id": profile_id})
        
        # Insert new recommendations
        if recommendation_data:
            await self.db.recommendations.insert_many(recommendation_data)
        
        return {
            "content_based": content_based,
            "collaborative": collaborative,
            "trending": trending,
            "continue_watching": continue_watching,
            "genre_recommendations": genre_recommendations
        }
    
    async def get_recommendations_for_profile(
        self, 
        profile_id: str, 
        algorithm: Optional[str] = None, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get stored recommendations for a profile."""
        query = {"profile_id": profile_id}
        if algorithm:
            query["algorithm_used"] = algorithm
        
        recommendations = await self.db.recommendations.find(query).sort("score", -1).limit(limit).to_list(None)
        
        # Get content details
        content_ids = [rec["content_id"] for rec in recommendations]
        content_list = await self.db.content.find({"id": {"$in": content_ids}}).to_list(None)
        content_dict = {content["id"]: content for content in content_list}
        
        # Combine recommendations with content details
        result = []
        for rec in recommendations:
            content = content_dict.get(rec["content_id"])
            if content:
                result.append({
                    "recommendation": rec,
                    "content": content
                })
        
        return result