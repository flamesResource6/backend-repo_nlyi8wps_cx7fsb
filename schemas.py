"""
Database Schemas for Gulf Global Tours

Each Pydantic model below represents a MongoDB collection. The collection
name is the lowercase of the class name (e.g., Trip -> "trip").
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date

class Trip(BaseModel):
    title: str = Field(..., description="Trip display name")
    trip_type: str = Field(..., description="Unique key, e.g., 'dimaniyat' or 'sunset'")
    description: str = Field(..., description="Detailed description of the trip")
    location: str = Field(..., description="Primary location")
    price_per_person: float = Field(..., ge=0, description="Price per guest in OMR")
    capacity: int = Field(..., ge=1, description="Maximum guests per departure")
    duration_hours: float = Field(..., gt=0, description="Duration in hours")
    highlights: List[str] = Field(default_factory=list, description="Key highlights")
    includes: List[str] = Field(default_factory=list, description="What’s included")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    is_active: bool = Field(default=True)

class Booking(BaseModel):
    trip_type: str = Field(..., description="Trip key the booking is for")
    name: str
    email: EmailStr
    phone: str
    date: date
    people_count: int = Field(..., ge=1)
    notes: Optional[str] = None
    status: str = Field(default="pending", description="pending|confirmed|cancelled")

class Review(BaseModel):
    name: str
    rating: int = Field(..., ge=1, le=5)
    comment: str
    trip_type: Optional[str] = Field(default=None, description="Optional trip key")

class FAQ(BaseModel):
    question: str
    answer: str
    category: Optional[str] = Field(default="general")
    order: int = Field(default=0)

class Inquiry(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
