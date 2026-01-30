# FastAPI Skill

**Version**: 1.0
**Last Updated**: 2026-01-31
**Compliance**: FastAPI 0.128.0+, Pydantic v2, SQLAlchemy 2.0 async

---

Production-tested patterns for FastAPI with Pydantic v2, SQLAlchemy 2.0 async, JWT authentication, and Firestore integration.

## Latest Versions (verified January 2026)

- **FastAPI**: 0.128.0
- **Pydantic**: 2.11.7
- **SQLAlchemy**: 2.0.30 (optional - for SQL databases)
- **Uvicorn**: 0.35.0
- **python-jose**: 3.3.0
- **Firebase Admin SDK**: 6.5.0 (for Firestore)

## Requirements

- Python 3.10+ (Python 3.8 support dropped in FastAPI 0.125.0)
- Pydantic v2.7.0+ (Pydantic v1 support completely removed in FastAPI 0.128.0)
- **uv** package manager (recommended)

---

## Quick Start

### Project Setup with uv

```bash
# Create project
uv init my-api
cd my-api

# Add dependencies
uv add fastapi[standard] python-jose[cryptography] passlib[bcrypt]

# For Firestore
uv add firebase-admin

# For SQL databases (optional)
uv add sqlalchemy[asyncio] aiosqlite

# Run development server
uv run fastapi dev src/main.py
```

### Minimal Working Example

```python
# src/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="My API")

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/items")
async def create_item(item: Item):
    return item
```

**Run**: `uv run fastapi dev src/main.py`

**Docs available at**: http://127.0.0.1:8000/docs

---

## Project Structure (Domain-Based)

For maintainable projects, organize by domain not file type:

```
my-api/
├── pyproject.toml
├── .env                     # Environment variables (gitignored)
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Global settings
│   ├── database.py          # Database connection (Firestore/SQL)
│   │
│   ├── auth/                # Auth domain
│   │   ├── __init__.py
│   │   ├── router.py        # Auth endpoints
│   │   ├── schemas.py       # Pydantic models
│   │   ├── models.py        # Data models
│   │   ├── service.py       # Business logic
│   │   └── dependencies.py  # Auth dependencies
│   │
│   ├── items/               # Items domain
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   └── service.py
│   │
│   └── shared/              # Shared utilities
│       ├── __init__.py
│       └── exceptions.py
└── tests/
    └── test_main.py
```

---

## Core Patterns

### Pydantic Schemas (Validation)

```python
# src/items/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

class ItemStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: float = Field(..., gt=0, description="Price must be positive")
    status: ItemStatus = ItemStatus.DRAFT

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    status: ItemStatus | None = None

class ItemResponse(ItemBase):
    id: str  # Firestore document ID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Key Points:**
- Use `Field()` for validation constraints
- Separate Create/Update/Response schemas
- `from_attributes=True` enables model conversion
- Use `str | None` (Python 3.10+) not `Optional[str]`

---

### Firestore Integration

```python
# src/database.py
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import AsyncClient
from typing import AsyncGenerator

# Initialize Firebase Admin
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Async Firestore client
def get_firestore_client() -> AsyncClient:
    return firestore.AsyncClient()

async def get_db() -> AsyncGenerator[AsyncClient, None]:
    """Dependency for Firestore client"""
    db = get_firestore_client()
    try:
        yield db
    finally:
        # Firestore client cleanup (if needed)
        pass
```

**Environment Variable Approach (Recommended for Production)**:

```python
# src/database.py
import os
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import AsyncClient

def initialize_firebase():
    """Initialize Firebase with environment-based credentials"""
    if not firebase_admin._apps:
        # Use GOOGLE_APPLICATION_CREDENTIALS environment variable
        # or Application Default Credentials (ADC)
        firebase_admin.initialize_app()

def get_firestore_client() -> AsyncClient:
    initialize_firebase()
    return firestore.AsyncClient()
```

**Firestore Service Layer**:

```python
# src/items/service.py
from google.cloud.firestore_v1 import AsyncClient
from src.items import schemas
from datetime import datetime

class ItemService:
    COLLECTION = "items"

    @staticmethod
    async def create(db: AsyncClient, item_in: schemas.ItemCreate, user_id: str) -> dict:
        """Create a new item in Firestore"""
        doc_ref = db.collection(ItemService.COLLECTION).document()
        item_data = item_in.model_dump()
        item_data.update({
            "id": doc_ref.id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        await doc_ref.set(item_data)
        return item_data

    @staticmethod
    async def get(db: AsyncClient, item_id: str) -> dict | None:
        """Get item by ID"""
        doc = await db.collection(ItemService.COLLECTION).document(item_id).get()
        if not doc.exists:
            return None
        return doc.to_dict()

    @staticmethod
    async def list_by_user(db: AsyncClient, user_id: str, limit: int = 100) -> list[dict]:
        """List items for a user"""
        docs = db.collection(ItemService.COLLECTION)\
            .where("user_id", "==", user_id)\
            .limit(limit)\
            .stream()

        items = []
        async for doc in docs:
            items.append(doc.to_dict())
        return items

    @staticmethod
    async def update(db: AsyncClient, item_id: str, item_in: schemas.ItemUpdate) -> dict | None:
        """Update an item"""
        doc_ref = db.collection(ItemService.COLLECTION).document(item_id)
        doc = await doc_ref.get()

        if not doc.exists:
            return None

        update_data = item_in.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        await doc_ref.update(update_data)

        updated_doc = await doc_ref.get()
        return updated_doc.to_dict()

    @staticmethod
    async def delete(db: AsyncClient, item_id: str) -> bool:
        """Delete an item"""
        doc_ref = db.collection(ItemService.COLLECTION).document(item_id)
        doc = await doc_ref.get()

        if not doc.exists:
            return False

        await doc_ref.delete()
        return True
```

---

### Router Pattern

```python
# src/items/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1 import AsyncClient

from src.database import get_db
from src.items import schemas, service
from src.auth.dependencies import get_current_user
from src.auth.models import User

router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_model=list[schemas.ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncClient = Depends(get_db)
):
    """List user's items"""
    items = await service.ItemService.list_by_user(db, current_user.id, limit)
    return items

@router.get("/{item_id}", response_model=schemas.ItemResponse)
async def get_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncClient = Depends(get_db)
):
    """Get a specific item"""
    item = await service.ItemService.get(db, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Authorization check
    if item["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return item

@router.post("", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: schemas.ItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncClient = Depends(get_db)
):
    """Create a new item"""
    item = await service.ItemService.create(db, item_in, current_user.id)
    return item

@router.patch("/{item_id}", response_model=schemas.ItemResponse)
async def update_item(
    item_id: str,
    item_in: schemas.ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncClient = Depends(get_db)
):
    """Update an item"""
    # Check existence and authorization
    existing = await service.ItemService.get(db, item_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    if existing["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    item = await service.ItemService.update(db, item_id, item_in)
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncClient = Depends(get_db)
):
    """Delete an item"""
    # Check existence and authorization
    existing = await service.ItemService.get(db, item_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    if existing["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await service.ItemService.delete(db, item_id)
    return None
```

---

### Main App

```python
# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import initialize_firebase
from src.items.router import router as items_router
from src.auth.router import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Firebase
    initialize_firebase()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(title="My API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(items_router)
```

---

## JWT Authentication

### Auth Schemas

```python
# src/auth/schemas.py
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: str | None = None
```

### Auth Service

```python
# src/auth/service.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict | None:
    """Decode a JWT token"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        return None
```

### Auth Dependencies

```python
# src/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from google.cloud.firestore_v1 import AsyncClient

from src.database import get_db
from src.auth import service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class User:
    """User model for dependency injection"""
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncClient = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = service.decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Get user from Firestore
    doc = await db.collection("users").document(user_id).get()
    if not doc.exists:
        raise credentials_exception

    user_data = doc.to_dict()
    return User(id=doc.id, email=user_data["email"])
```

### Auth Router

```python
# src/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from google.cloud.firestore_v1 import AsyncClient
from datetime import timedelta

from src.database import get_db
from src.auth import schemas, service
from src.auth.dependencies import get_current_user, User
from src.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserResponse)
async def register(
    user_in: schemas.UserCreate,
    db: AsyncClient = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    users = db.collection("users").where("email", "==", user_in.email).limit(1)
    existing = [doc async for doc in users.stream()]

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    doc_ref = db.collection("users").document()
    user_data = {
        "id": doc_ref.id,
        "email": user_in.email,
        "hashed_password": service.hash_password(user_in.password)
    }
    await doc_ref.set(user_data)

    return schemas.UserResponse(id=doc_ref.id, email=user_in.email)

@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncClient = Depends(get_db)
):
    """Login and get access token"""
    # Find user by email
    users = db.collection("users").where("email", "==", form_data.username).limit(1)
    user_docs = [doc async for doc in users.stream()]

    if not user_docs:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    user_doc = user_docs[0]
    user_data = user_doc.to_dict()

    # Verify password
    if not service.verify_password(form_data.password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = service.create_access_token(
        data={"sub": user_doc.id},
        expires_delta=access_token_expires
    )

    return schemas.Token(access_token=access_token)

@router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user"""
    return schemas.UserResponse(id=current_user.id, email=current_user.email)
```

---

## Configuration

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "My API"
    API_VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Firebase
    GOOGLE_APPLICATION_CREDENTIALS: str | None = None
    FIREBASE_PROJECT_ID: str | None = None

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

**Create `.env`:**

```bash
# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Firebase
GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
FIREBASE_PROJECT_ID=your-project-id

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
```

---

## Critical Rules

### Always Do

1. **Separate Pydantic schemas from data models** - Different jobs, different files
2. **Use async for I/O operations** - Database, HTTP calls, file access
3. **Validate with Pydantic `Field()`** - Constraints, defaults, descriptions
4. **Use dependency injection** - `Depends()` for database, auth, validation
5. **Return proper status codes** - 201 for create, 204 for delete, etc.

### Never Do

1. **Never use blocking calls in async routes** - No `time.sleep()`, use `asyncio.sleep()`
2. **Never put business logic in routes** - Use service layer
3. **Never hardcode secrets** - Use environment variables
4. **Never skip validation** - Always use Pydantic schemas
5. **Never use `*` in CORS origins for production** - Specify exact origins

---

## Known Issues Prevention

This skill prevents **7 documented issues** from official FastAPI GitHub and release notes.

### Issue #1: Form Data Loses Field Set Metadata

**Error**: `model.model_fields_set` includes default values when using `Form()`
**Source**: [GitHub Issue #13399](https://github.com/fastapi/fastapi/issues/13399)

**Why It Happens**: Form data parsing preloads default values and passes them to the validator, making it impossible to distinguish between fields explicitly set by the user and fields using defaults. This bug ONLY affects Form data, not JSON body data.

**Prevention:**

```python
# ✗ AVOID: Pydantic model with Form when you need field_set metadata
from typing import Annotated
from fastapi import Form

@app.post("/form")
async def endpoint(model: Annotated[MyModel, Form()]):
    fields = model.model_fields_set  # Unreliable! ❌

# ✓ USE: Individual form fields or JSON body instead
@app.post("/form-individual")
async def endpoint(
    field_1: Annotated[bool, Form()] = True,
    field_2: Annotated[str | None, Form()] = None
):
    # You know exactly what was provided ✓

# ✓ OR: Use JSON body when metadata matters
@app.post("/json")
async def endpoint(model: MyModel):
    fields = model.model_fields_set  # Works correctly ✓
```

---

### Issue #2: BackgroundTasks Silently Overwritten by Custom Response

**Error**: Background tasks added via `BackgroundTasks` dependency don't run
**Source**: [GitHub Issue #11215](https://github.com/fastapi/fastapi/issues/11215)

**Why It Happens**: When you return a custom `Response` with a `background` parameter, it overwrites all tasks added to the injected `BackgroundTasks` dependency. This is not documented and causes silent failures.

**Prevention:**

```python
# ✗ WRONG: Mixing both mechanisms
from fastapi import BackgroundTasks
from starlette.responses import Response, BackgroundTask

@app.get("/")
async def endpoint(tasks: BackgroundTasks):
    tasks.add_task(send_email)  # This will be lost! ❌
    return Response(
        content="Done",
        background=BackgroundTask(log_event)  # Only this runs
    )

# ✓ RIGHT: Use only BackgroundTasks dependency
@app.get("/")
async def endpoint(tasks: BackgroundTasks):
    tasks.add_task(send_email)
    tasks.add_task(log_event)
    return {"status": "done"}  # All tasks run ✓

# ✓ OR: Use only Response background (but can't inject dependencies)
@app.get("/")
async def endpoint():
    return Response(
        content="Done",
        background=BackgroundTask(log_event)
    )
```

**Rule**: Pick ONE mechanism and stick with it. Don't mix injected `BackgroundTasks` with `Response(background=...)`.

---

### Issue #3: Optional Form Fields Break with TestClient (Regression)

**Error**: `422: "Input should be 'abc' or 'def'"` for optional `Literal` fields
**Source**: [GitHub Issue #12245](https://github.com/fastapi/fastapi/issues/12245)

**Why It Happens**: Starting in FastAPI 0.114.0, optional form fields with `Literal` types fail validation when passed `None` via `TestClient`. Worked in 0.113.0.

**Prevention:**

```python
from typing import Annotated, Literal, Optional
from fastapi import Form
from fastapi.testclient import TestClient

# ✗ PROBLEMATIC: Optional Literal with Form (breaks in 0.114.0+)
@app.post("/")
async def endpoint(
    attribute: Annotated[Optional[Literal["abc", "def"]], Form()]
):
    return {"attribute": attribute}

client = TestClient(app)
data = {"attribute": None}  # or omit the field
response = client.post("/", data=data)  # Returns 422 ❌

# ✓ WORKAROUND 1: Don't pass None explicitly, omit the field
data = {}  # Omit instead of None
response = client.post("/", data=data)  # Works ✓

# ✓ WORKAROUND 2: Avoid Literal types with optional form fields
@app.post("/")
async def endpoint(attribute: Annotated[str | None, Form()] = None):
    # Validate in application logic instead
    if attribute and attribute not in ["abc", "def"]:
        raise HTTPException(400, "Invalid attribute")
```

---

### Issue #4: Pydantic Json Type Doesn't Work with Form Data

**Error**: "JSON object must be str, bytes or bytearray"
**Source**: [GitHub Issue #10997](https://github.com/fastapi/fastapi/issues/10997)

**Why It Happens**: Using Pydantic's `Json` type directly with `Form()` fails. You must accept the field as `str` and parse manually.

**Prevention:**

```python
from typing import Annotated
from fastapi import Form
from pydantic import Json, BaseModel

# ✗ WRONG: Json type directly with Form
@app.post("/broken")
async def broken(json_list: Annotated[Json[list[str]], Form()]) -> list[str]:
    return json_list  # Returns 422 ❌

# ✓ RIGHT: Accept as str, parse with Pydantic
class JsonListModel(BaseModel):
    json_list: Json[list[str]]

@app.post("/working")
async def working(json_list: Annotated[str, Form()]) -> list[str]:
    model = JsonListModel(json_list=json_list)  # Pydantic parses here
    return model.json_list  # Works ✓
```

---

### Issue #5: Annotated with ForwardRef Breaks OpenAPI Generation

**Error**: Missing or incorrect OpenAPI schema for dependency types
**Source**: [GitHub Issue #13056](https://github.com/fastapi/fastapi/issues/13056)

**Why It Happens**: When using `Annotated` with `Depends()` and a forward reference (`from __future__ import annotations`), OpenAPI schema generation fails or produces incorrect schemas.

**Prevention:**

```python
# ✗ PROBLEMATIC: Forward reference with Depends
from __future__ import annotations
from dataclasses import dataclass
from typing import Annotated
from fastapi import Depends, FastAPI

app = FastAPI()

def get_potato() -> Potato:  # Forward reference
    return Potato(color='red', size=10)

@app.get('/')
async def read_root(potato: Annotated[Potato, Depends(get_potato)]):
    return {'Hello': 'World'}
# OpenAPI schema doesn't include Potato definition correctly ❌

@dataclass
class Potato:
    color: str
    size: int

# ✓ WORKAROUND 1: Don't use __future__ annotations in route files
# Remove: from __future__ import annotations

# ✓ WORKAROUND 2: Use string literals for type hints
def get_potato() -> "Potato":
    return Potato(color='red', size=10)

# ✓ WORKAROUND 3: Define classes before they're used in dependencies
@dataclass
class Potato:
    color: str
    size: int

def get_potato() -> Potato:  # Now works ✓
    return Potato(color='red', size=10)
```

---

### Issue #6: Pydantic v2 Path Parameter Union Type Breaking Change

**Error**: Path parameters with `int | str` always parse as `str` in Pydantic v2
**Source**: [GitHub Issue #11251](https://github.com/fastapi/fastapi/issues/11251)

**Why It Happens**: Major breaking change when migrating from Pydantic v1 to v2. Union types with `str` in path/query parameters now always parse as `str` (worked correctly in v1).

**Prevention:**

```python
from uuid import UUID

# ✗ PROBLEMATIC: Union with str in path parameter
@app.get("/int/{path}")
async def int_path(path: int | str):
    return str(type(path))
    # Pydantic v1: returns <class 'int'> for "123"
    # Pydantic v2: returns <class 'str'> for "123" ❌

@app.get("/uuid/{path}")
async def uuid_path(path: UUID | str):
    return str(type(path))
    # Pydantic v1: returns <class 'uuid.UUID'> for valid UUID
    # Pydantic v2: returns <class 'str'> ❌

# ✓ RIGHT: Avoid union types with str in path/query parameters
@app.get("/int/{path}")
async def int_path(path: int):
    return str(type(path))  # Works correctly ✓

# ✓ ALTERNATIVE: Use validators if type coercion needed
from pydantic import field_validator

class PathParams(BaseModel):
    path: int | str

    @field_validator('path')
    def coerce_to_int(cls, v):
        if isinstance(v, str) and v.isdigit():
            return int(v)
        return v
```

---

### Issue #7: ValueError in field_validator Returns 500 Instead of 422

**Error**: 500 Internal Server Error when raising `ValueError` in custom validators
**Source**: [GitHub Discussion #10779](https://github.com/fastapi/fastapi/discussions/10779)

**Why It Happens**: When raising `ValueError` inside a Pydantic `@field_validator` with Form fields, FastAPI returns 500 Internal Server Error instead of the expected 422 Unprocessable Entity validation error.

**Prevention:**

```python
from typing import Annotated
from fastapi import Form
from pydantic import BaseModel, field_validator, ValidationError, Field

# ✗ WRONG: ValueError in validator
class MyForm(BaseModel):
    value: int

    @field_validator('value')
    def validate_value(cls, v):
        if v < 0:
            raise ValueError("Value must be positive")  # Returns 500! ❌
        return v

# ✓ RIGHT 1: Raise ValidationError instead
class MyForm(BaseModel):
    value: int

    @field_validator('value')
    def validate_value(cls, v):
        if v < 0:
            raise ValidationError("Value must be positive")  # Returns 422 ✓
        return v

# ✓ RIGHT 2: Use Pydantic's built-in constraints
class MyForm(BaseModel):
    value: Annotated[int, Field(gt=0)]  # Built-in validation, returns 422 ✓
```

---

## Common Errors & Fixes

### 422 Unprocessable Entity

**Cause**: Request body doesn't match Pydantic schema

**Debug:**
- Check `/docs` endpoint - test there first
- Verify JSON structure matches schema
- Check required vs optional fields

**Fix**: Add custom validation error handler:

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )
```

---

### CORS Errors

**Cause**: Missing or misconfigured CORS middleware

**Fix:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Not "*" in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Async Blocking Event Loop

**Cause**: Blocking call in async route (e.g., `time.sleep()`, sync database client, CPU-bound operations)

**Symptoms (production-scale):**
- Throughput plateaus far earlier than expected
- Latency "balloons" as concurrency increases
- Request pattern looks almost serial under load
- Requests queue indefinitely when event loop is saturated

**Fix**: Use async alternatives:

```python
# ✗ WRONG: Blocks event loop
import time

@app.get("/users")
async def get_users():
    time.sleep(0.1)  # Even small blocking adds up at scale!
    return result

# ✓ RIGHT 1: Use asyncio.sleep
import asyncio

@app.get("/users")
async def get_users():
    await asyncio.sleep(0.1)  # Non-blocking ✓
    return result

# ✓ RIGHT 2: Use def (not async def) for CPU-bound routes
# FastAPI runs def routes in thread pool automatically
@app.get("/cpu-heavy")
def cpu_heavy_task():  # Note: def not async def
    return expensive_cpu_work()  # Runs in thread pool ✓

# ✓ RIGHT 3: Use run_in_executor for blocking calls in async routes
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

@app.get("/mixed")
async def mixed_task():
    # Run blocking function in thread pool
    result = await asyncio.get_event_loop().run_in_executor(
        executor,
        blocking_function  # Your blocking function
    )
    return result
```

---

### "Field required" for Optional Fields

**Cause**: Using `Optional[str]` without default

**Fix:**

```python
# ✗ Wrong
description: Optional[str]  # Still required!

# ✓ Right
description: str | None = None  # Optional with default
```

---

## Testing

```python
# tests/test_main.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_item(client):
    response = await client.post(
        "/items",
        json={"name": "Test", "price": 9.99}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
```

**Run**: `uv run pytest`

---

## Deployment

### Uvicorn (Development)

```bash
uv run fastapi dev src/main.py
```

### Uvicorn (Production)

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Gunicorn + Uvicorn (Production with workers)

```bash
uv add gunicorn
uv run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [uv Package Manager](https://github.com/astral-sh/uv)

---

**最終更新**: 2026-01-31
**次回レビュー**: MVP開発開始時
