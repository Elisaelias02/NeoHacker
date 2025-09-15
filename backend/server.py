from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import re
import aiofiles
import magic
from PIL import Image
import hashlib
import shutil

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with Atlas compatibility
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'test_database')

# Configure MongoDB client for Atlas compatibility
client = AsyncIOMotorClient(
    mongo_url,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    socketTimeoutMS=0,
    maxPoolSize=10,
    retryWrites=True,
    w='majority'
)
db = client[db_name]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# JWT settings
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', 60))

# File upload settings
UPLOAD_PATH = Path(os.environ.get('UPLOAD_PATH', '/app/backend/uploads'))
MAX_FILE_SIZE_MB = int(os.environ.get('MAX_FILE_SIZE_MB', 10))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_PDF_EXTENSIONS = {'.pdf'}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_PDF_EXTENSIONS

# Create upload directories
UPLOAD_PATH.mkdir(exist_ok=True)
(UPLOAD_PATH / 'images').mkdir(exist_ok=True)
(UPLOAD_PATH / 'pdfs').mkdir(exist_ok=True)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# User Models with Role System
class UserRole(str):
    ADMIN = "admin"
    USER = "user"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashed_password: str
    role: str = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

    @validator('email')
    def validate_email(cls, v):
        if len(v) > 254:
            raise ValueError('Email too long')
        return v.lower().strip()

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Resource Models
class ResourceType(str):
    PDF = "pdf"
    IMAGE = "image" 
    LINK = "link"

class Resource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: str  # pdf, image, link
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    external_url: Optional[str] = None
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    is_featured: bool = False
    uploaded_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ResourceCreate(BaseModel):
    name: str
    description: str
    external_url: Optional[str] = None
    is_featured: bool = False

    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Resource name must be at least 3 characters long')
        if len(v) > 100:
            raise ValueError('Resource name too long (max 100 characters)')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Description must be at least 10 characters long')
        if len(v) > 500:
            raise ValueError('Description too long (max 500 characters)')
        return v.strip()

class ResourceResponse(BaseModel):
    id: str
    name: str
    description: str
    type: str
    file_url: Optional[str] = None
    external_url: Optional[str] = None
    file_size: Optional[int] = None
    is_featured: bool
    uploaded_by: str
    created_at: datetime

# Post Models (updated to include author validation)
class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    tags: List[str] = []
    author: str = "Anonymous"
    author_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PostCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []

    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Title must be at least 5 characters long')
        if len(v) > 200:
            raise ValueError('Title too long (max 200 characters)')
        if '<' in v or '>' in v or '"' in v or "'" in v:
            raise ValueError('Title contains invalid characters')
        return v.strip()

    @validator('content')
    def validate_content(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Content must be at least 10 characters long')
        if len(v) > 10000:
            raise ValueError('Content too long (max 10000 characters)')
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        cleaned_tags = []
        for tag in v:
            tag = tag.strip().lower()
            if len(tag) > 50:
                raise ValueError('Tag too long (max 50 characters)')
            if re.match(r'^[a-z0-9-_]+$', tag):
                cleaned_tags.append(tag)
        return cleaned_tags

# Comment Models (updated to include author validation)
class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    content: str
    author: str = "Anonymous"
    author_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CommentCreate(BaseModel):
    post_id: str
    content: str

    @validator('content')
    def validate_content(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Comment cannot be empty')
        if len(v) > 1000:
            raise ValueError('Comment too long (max 1000 characters)')
        return v.strip()

# Security functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_user_by_email(email: str):
    user = await db.users.find_one({"email": email})
    if user:
        return User(**parse_from_mongo(user))
    return None

async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )
    return current_user

# File handling functions
def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and other attacks"""
    # Remove path components and keep only the filename
    filename = os.path.basename(filename)
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:95] + ext
    return filename

def get_file_hash(file_path: Path) -> str:
    """Generate SHA-256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

async def validate_file(file: UploadFile) -> tuple[bool, str]:
    """Validate uploaded file for security"""
    # Check file size
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    
    if len(content) > MAX_FILE_SIZE_BYTES:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check MIME type using python-magic
    mime_type = magic.from_buffer(content, mime=True)
    
    if file_ext in ALLOWED_IMAGE_EXTENSIONS:
        if not mime_type.startswith('image/'):
            return False, "Invalid image file"
    elif file_ext in ALLOWED_PDF_EXTENSIONS:
        if mime_type != 'application/pdf':
            return False, "Invalid PDF file"
    
    return True, "File is valid"

async def save_uploaded_file(file: UploadFile, subdir: str) -> tuple[Path, str]:
    """Save uploaded file securely"""
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Generate unique filename with UUID prefix
    unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
    
    # Determine file path
    file_path = UPLOAD_PATH / subdir / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Generate file hash
    file_hash = get_file_hash(file_path)
    
    return file_path, file_hash

# Helper functions
def prepare_for_mongo(data):
    if isinstance(data.get('created_at'), datetime):
        data['created_at'] = data['created_at'].isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item.get('created_at'), str):
        item['created_at'] = datetime.fromisoformat(item['created_at'])
    return item

# Authentication Routes
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

@auth_router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user (first user becomes admin)
    user_count = await db.users.count_documents({})
    role = UserRole.ADMIN if user_count == 0 else UserRole.USER
    
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        role=role
    )
    
    user_dict = prepare_for_mongo(user.dict())
    await db.users.insert_one(user_dict)
    
    return UserResponse(**user.dict())

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

# Resource Routes
resources_router = APIRouter(prefix="/resources", tags=["resources"])

@resources_router.post("/upload", response_model=ResourceResponse)
async def upload_resource(
    name: str = Form(...),
    description: str = Form(...),
    is_featured: bool = Form(False),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin)
):
    # Validate input data
    try:
        resource_data = ResourceCreate(
            name=name,
            description=description,
            is_featured=is_featured
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Validate file
    is_valid, error_msg = await validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Determine resource type and subdirectory
    file_ext = Path(file.filename).suffix.lower()
    if file_ext in ALLOWED_IMAGE_EXTENSIONS:
        resource_type = ResourceType.IMAGE
        subdir = "images"
    elif file_ext in ALLOWED_PDF_EXTENSIONS:
        resource_type = ResourceType.PDF
        subdir = "pdfs"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Save file
    try:
        file_path, file_hash = await save_uploaded_file(file, subdir)
        file_size = file_path.stat().st_size
        
        # Create resource record
        resource = Resource(
            name=resource_data.name,
            description=resource_data.description,
            type=resource_type,
            file_path=str(file_path),
            file_url=f"/api/resources/download/{file_path.name}",
            file_size=file_size,
            file_hash=file_hash,
            is_featured=resource_data.is_featured,
            uploaded_by=current_user.email
        )
        
        resource_dict = prepare_for_mongo(resource.dict())
        await db.resources.insert_one(resource_dict)
        
        return ResourceResponse(**resource.dict())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

@resources_router.post("/link", response_model=ResourceResponse)
async def create_link_resource(
    resource_data: ResourceCreate,
    current_user: User = Depends(get_current_admin)
):
    if not resource_data.external_url:
        raise HTTPException(status_code=400, detail="External URL is required for link resources")
    
    # Validate URL format
    if not re.match(r'https?://.*', resource_data.external_url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    resource = Resource(
        name=resource_data.name,
        description=resource_data.description,
        type=ResourceType.LINK,
        external_url=resource_data.external_url,
        is_featured=resource_data.is_featured,
        uploaded_by=current_user.email
    )
    
    resource_dict = prepare_for_mongo(resource.dict())
    await db.resources.insert_one(resource_dict)
    
    return ResourceResponse(**resource.dict())

@resources_router.get("/", response_model=List[ResourceResponse])
async def get_resources(
    resource_type: Optional[str] = None,
    search: Optional[str] = None,
    featured_only: bool = False
):
    query = {}
    
    if resource_type and resource_type in [ResourceType.PDF, ResourceType.IMAGE, ResourceType.LINK]:
        query["type"] = resource_type
    
    if featured_only:
        query["is_featured"] = True
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Sort: featured first, then by creation date
    sort_criteria = [("is_featured", -1), ("created_at", -1)]
    
    resources = await db.resources.find(query).sort(sort_criteria).to_list(100)
    
    return [ResourceResponse(**parse_from_mongo(resource)) for resource in resources]

@resources_router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: str):
    resource = await db.resources.find_one({"id": resource_id})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return ResourceResponse(**parse_from_mongo(resource))

@resources_router.delete("/{resource_id}")
async def delete_resource(resource_id: str, current_user: User = Depends(get_current_admin)):
    resource = await db.resources.find_one({"id": resource_id})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Delete file if it exists
    if resource.get("file_path"):
        file_path = Path(resource["file_path"])
        if file_path.exists():
            file_path.unlink()
    
    # Delete database record
    await db.resources.delete_one({"id": resource_id})
    return {"message": "Resource deleted successfully"}

@resources_router.get("/download/{filename}")
async def download_file(filename: str):
    # Find file in upload directories
    for subdir in ["images", "pdfs"]:
        file_path = UPLOAD_PATH / subdir / filename
        if file_path.exists():
            return FileResponse(
                path=str(file_path),
                filename=filename,
                headers={"Content-Disposition": "attachment"}
            )
    
    raise HTTPException(status_code=404, detail="File not found")

# Main Routes
@api_router.get("/")
async def root():
    return {"message": "NeonSec Hacker Blog API v2.1 - Now with Resources!"}

# Health check endpoint for Kubernetes
@api_router.get("/health")
async def health_check():
    try:
        # Test database connection
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.1"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

# Root health check (without /api prefix for load balancer)
@app.get("/health")
async def app_health_check():
    try:
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.1"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

@api_router.post("/posts", response_model=Post)
async def create_post(post_data: PostCreate, current_user: User = Depends(get_current_user)):
    post = Post(
        **post_data.dict(),
        author=current_user.email.split('@')[0],
        author_id=current_user.id
    )
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
async def delete_post(post_id: str, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.get("author_id") != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    await db.posts.delete_one({"id": post_id})
    await db.comments.delete_many({"post_id": post_id})
    return {"message": "Post deleted successfully"}

@api_router.post("/comments", response_model=Comment)
async def create_comment(comment_data: CommentCreate, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": comment_data.post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment = Comment(
        **comment_data.dict(),
        author=current_user.email.split('@')[0],
        author_id=current_user.id
    )
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

# Include routers
api_router.include_router(auth_router)
api_router.include_router(resources_router)
app.include_router(api_router)

# Mount static files for downloads
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_PATH)), name="uploads")

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