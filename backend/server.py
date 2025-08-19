from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    tags: List[str] = []
    author: str = "Anonymous"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PostCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []
    author: str = "Anonymous"

class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    content: str
    author: str = "Anonymous"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CommentCreate(BaseModel):
    post_id: str
    content: str
    author: str = "Anonymous"

# Helper functions
def prepare_for_mongo(data):
    if isinstance(data.get('created_at'), datetime):
        data['created_at'] = data['created_at'].isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item.get('created_at'), str):
        item['created_at'] = datetime.fromisoformat(item['created_at'])
    return item

# Routes
@api_router.get("/")
async def root():
    return {"message": "NeonSec Hacker Blog API v1.0"}

@api_router.post("/posts", response_model=Post)
async def create_post(post_data: PostCreate):
    post = Post(**post_data.dict())
    post_dict = prepare_for_mongo(post.dict())
    await db.posts.insert_one(post_dict)
    return post

@api_router.get("/posts", response_model=List[Post])
async def get_posts(tag: Optional[str] = None, search: Optional[str] = None):
    query = {}
    
    if tag:
        query["tags"] = {"$in": [tag]}
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]
    
    posts = await db.posts.find(query).sort("created_at", -1).to_list(100)
    return [Post(**parse_from_mongo(post)) for post in posts]

@api_router.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: str):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return Post(**parse_from_mongo(post))

@api_router.delete("/posts/{post_id}")
async def delete_post(post_id: str):
    result = await db.posts.delete_one({"id": post_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    # Also delete associated comments
    await db.comments.delete_many({"post_id": post_id})
    return {"message": "Post deleted successfully"}

@api_router.post("/comments", response_model=Comment)
async def create_comment(comment_data: CommentCreate):
    # Verify post exists
    post = await db.posts.find_one({"id": comment_data.post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment = Comment(**comment_data.dict())
    comment_dict = prepare_for_mongo(comment.dict())
    await db.comments.insert_one(comment_dict)
    return comment

@api_router.get("/comments/{post_id}", response_model=List[Comment])
async def get_comments(post_id: str):
    comments = await db.comments.find({"post_id": post_id}).sort("created_at", 1).to_list(100)
    return [Comment(**parse_from_mongo(comment)) for comment in comments]

@api_router.get("/tags")
async def get_popular_tags():
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    
    tags = await db.posts.aggregate(pipeline).to_list(20)
    return [{"tag": tag["_id"], "count": tag["count"]} for tag in tags]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()