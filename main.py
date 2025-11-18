import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Trip, Booking, Review, FAQ, Inquiry

app = FastAPI(title="Gulf Global Tours API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utilities
class ObjectIdStr(BaseModel):
    id: str


def oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")


@app.get("/")
def root():
    return {"service": "Gulf Global Tours API", "status": "ok"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Seed default data if empty
@app.post("/seed")
def seed():
    # Trips
    trips_col = db["trip"]
    if trips_col.count_documents({}) == 0:
        seed_trips = [
            Trip(
                title="Dimaniyat Island Day Trip",
                trip_type="dimaniyat",
                description="Explore the pristine Dimaniyat Islands aboard our 11.3m Looker 370 glass-bottom boat. Snorkel vibrant reefs, spot sea turtles, and enjoy a beach stop.",
                location="Dimaniyat Islands, Oman",
                price_per_person=35.0,
                capacity=20,
                duration_hours=5.0,
                highlights=[
                    "Snorkeling coral reefs",
                    "Sea turtles and marine life",
                    "Beachtime on a protected island",
                    "Glass-bottom reef viewing"
                ],
                includes=["Captain & crew", "Snorkel gear", "Water & soft drinks"],
                images=[
                    "/images/dimaniyat-1.jpg",
                    "/images/dimaniyat-2.jpg",
                    "/images/looker370.jpg"
                ],
            ).model_dump(),
            Trip(
                title="Muscat Sunset Cruise",
                trip_type="sunset",
                description="A golden-hour cruise along Muscat’s coastline aboard our Looker 370. Take in Al Alam Palace, Muttrah Corniche, and dramatic sea cliffs as the sun sets.",
                location="Muscat Coastline, Oman",
                price_per_person=20.0,
                capacity=10,
                duration_hours=2.0,
                highlights=[
                    "Golden hour views",
                    "Iconic Muscat landmarks",
                    "Relaxed vibes on calm waters",
                    "Great photo opportunities"
                ],
                includes=["Captain & crew", "Water & soft drinks"],
                images=[
                    "/images/sunset-1.jpg",
                    "/images/sunset-2.jpg",
                    "/images/looker370.jpg"
                ],
            ).model_dump(),
        ]
        trips_col.insert_many(seed_trips)

    # FAQs
    faq_col = db["faq"]
    if faq_col.count_documents({}) == 0:
        faq_col.insert_many([
            {"question": "Where do trips depart from?", "answer": "Muscat, Oman. Exact marina details shared upon booking.", "category": "general", "order": 1},
            {"question": "How many guests can join?", "answer": "Up to 18-20 for Dimaniyat and 8-10 for sunset trips.", "category": "capacity", "order": 2},
            {"question": "What should I bring?", "answer": "Sunscreen, hat, towel, and swimwear. We provide water, soft drinks, and snorkel gear for day trips.", "category": "prep", "order": 3},
            {"question": "Is the glass bottom safe?", "answer": "Yes. The Looker 370 is purpose-built with reinforced glass for reef viewing.", "category": "safety", "order": 4},
        ])

    return {"status": "ok"}


# Public content endpoints
@app.get("/trips")
def get_trips():
    trips = get_documents("trip")
    for t in trips:
        t["_id"] = str(t["_id"])  # jsonify
    return trips


@app.get("/faqs")
def get_faqs():
    faqs = get_documents("faq", {}, limit=100)
    for f in faqs:
        f["_id"] = str(f["_id"])  # jsonify
    # sort by order then question
    faqs.sort(key=lambda x: (x.get("order", 0), x.get("question", "")))
    return faqs


@app.get("/reviews")
def get_reviews():
    reviews = get_documents("review", {}, limit=50)
    for r in reviews:
        r["_id"] = str(r["_id"])  # jsonify
    return reviews


# Booking and inquiries
@app.post("/book")
def create_booking(payload: Booking):
    # Validate capacity against trips
    trip = db["trip"].find_one({"trip_type": payload.trip_type, "is_active": True})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if payload.people_count > trip.get("capacity", 0):
        raise HTTPException(status_code=400, detail=f"Maximum capacity is {trip.get('capacity')} for this trip")

    booking_id = create_document("booking", payload)
    return {"status": "received", "id": booking_id}


@app.post("/inquire")
def create_inquiry(payload: Inquiry):
    inquiry_id = create_document("inquiry", payload)
    return {"status": "received", "id": inquiry_id}


# Simple create-review endpoint
@app.post("/review")
def add_review(payload: Review):
    review_id = create_document("review", payload)
    return {"status": "received", "id": review_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
