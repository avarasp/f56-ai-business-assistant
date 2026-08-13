from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

Intent = Literal["sales", "products", "contacts", "unsupported"]

class RouteDecision(BaseModel):
    intent: Intent
    reason: str

class SalesQuery(BaseModel):
    metric: Literal[
        "copies",
        "gross_revenue",
        "fees",
        "net_revenue",
    ] = "copies"

    group_by: Literal[
        "none",
        "product",
        "country",
        "platform",
        "month",
        "year",
    ] = "none"

    date_from: date | None = None
    date_to: date | None = None

    product_name: str | None = None

    country_code: str | None = Field(
        default=None,
        min_length=2,
        max_length=2,
    )

    platform_name: str | None = None
    
class ProductQuery(BaseModel):
    product_name: str | None = None

class ContactQuery(BaseModel):
    email: str | None = None
    name_contains: str | None = None
    text_contains: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    limit: int = Field(default=20, ge=1, le=100)
