from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import Base
from app.schemas import (
    URLShortenRequest,
    URLShortenResponse,
    URLUpdateRequest,
    URLUpdateResponse,
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


@app.post(
    "/update/{update_id}",
    response_model=URLUpdateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def update_url(
    update_id: str, request: URLUpdateRequest, db: Session = Depends(get_db)
):
    """
    Update the URL for an existing shortcode using the update ID.
    """
    # Validate URL is present
    if not request.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Url not present"
        )

    # Check if update_id exists
    db_mapping = crud.get_url_mapping_by_update_id(db, update_id)
    if not db_mapping:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The provided update ID does not exist",
        )

    try:
        # Update the URL
        updated_mapping = crud.update_url_mapping(db, update_id, request.url)

        return URLUpdateResponse(shortcode=updated_mapping.shortcode)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="The provided url is invalid",
        )


@app.get("/", tags=["Root"])
async def root():
    return {"message": "URL Shortening Service", "version": "1.0.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
