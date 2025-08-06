from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import Base
from app.schemas import (
    URLShortenRequest,
    URLShortenResponse,
)
from app import crud
from app.utils import is_valid_shortcode

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortening Service",
    description="A scalable URL shortening service with custom shortcodes",
    version="1.0.0",
)


@app.post(
    "/shorten", response_model=URLShortenResponse, status_code=status.HTTP_201_CREATED
)
async def shorten_url(request: URLShortenRequest, db: Session = Depends(get_db)):
    """
    Shorten a URL with optional custom shortcode.

    If no shortcode is provided, generates a random 6-character shortcode.
    """
    # Validate URL is present (handled by Pydantic, but explicit check for error consistency)
    if not request.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Url not present"
        )

    # If shortcode is provided, validate it doesn't already exist
    if request.shortcode:
        if not is_valid_shortcode(request.shortcode):
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="The provided shortcode/url is invalid",
            )

        if crud.shortcode_exists(db, request.shortcode):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Shortcode already in use"
            )

    try:
        # Create the URL mapping
        db_mapping = crud.create_url_mapping(
            db=db, url=request.url, shortcode=request.shortcode
        )

        return URLShortenResponse(
            shortcode=db_mapping.shortcode, update_id=db_mapping.update_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="The provided shortcode/url is invalid",
        )
