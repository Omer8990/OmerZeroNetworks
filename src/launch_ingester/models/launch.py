"""
Pydantic Models for SpaceX Launch Data.

This module defines a set of Pydantic models that represent the structure of
the launch data returned by the SpaceX v4 API. These models are used to
validate and parse the JSON response from the API into typed Python objects.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class Fairings(BaseModel):
    """Data model for the fairings of a rocket."""
    reused: Optional[bool] = None
    recovery_attempt: Optional[bool] = None
    recovered: Optional[bool] = None
    ships: List[str] = []

class Patch(BaseModel):
    """Data model for mission patch images."""
    small: Optional[str] = None
    large: Optional[str] = None

class Reddit(BaseModel):
    """Data model for Reddit links related to the launch."""
    campaign: Optional[str] = None
    launch: Optional[str] = None
    media: Optional[str] = None
    recovery: Optional[str] = None

class Flickr(BaseModel):
    """Data model for Flickr image links."""
    small: List[str] = []
    original: List[str] = []

class Links(BaseModel):
    """Data model for all links associated with a launch."""
    patch: Patch
    reddit: Reddit
    flickr: Flickr
    presskit: Optional[str] = None
    webcast: Optional[str] = None
    youtube_id: Optional[str] = Field(None, alias='youtube_id')
    article: Optional[str] = None
    wikipedia: Optional[str] = None

class Core(BaseModel):
    """Data model for a rocket core used in a launch."""
    core: Optional[str] = None
    flight: Optional[int] = None
    gridfins: Optional[bool] = None
    legs: Optional[bool] = None
    reused: Optional[bool] = None
    landing_attempt: Optional[bool] = None
    landing_success: Optional[bool] = None
    landing_type: Optional[str] = None
    landpad: Optional[str] = None

class Payload(BaseModel):
    """Data model for a payload carried by a launch."""
    name: str
    type: Optional[str] = None
    mass_kg: Optional[float] = None
    mass_lbs: Optional[float] = None
    orbit: Optional[str] = None
    customers: List[str] = []
    nationalities: List[str] = []
    manufacturers: List[str] = []
    id: str

class Launch(BaseModel):
    """
    The main Pydantic model representing a single SpaceX launch.
    
    This model captures all the details for a launch as returned by the
    SpaceX v4 API's /launches/query endpoint.
    """
    fairings: Optional[Fairings] = None
    links: Links
    static_fire_date_utc: Optional[str] = None
    static_fire_date_unix: Optional[int] = None
    net: bool
    window: Optional[int] = None
    rocket: str
    success: Optional[bool] = None
    failures: List = []
    details: Optional[str] = None
    crew: List = []
    ships: List[str] = []
    capsules: List[str] = []
    payloads: List[Payload] = []
    launchpad: str
    flight_number: int
    name: str
    date_utc: str
    date_unix: int
    date_local: str
    date_precision: str
    upcoming: bool
    cores: List[Core] = []
    auto_update: bool
    tbd: bool
    launch_library_id: Optional[str] = None
    id: str
