from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class ShipmentStatusEnum(str, Enum):
    """Shipment status enumeration."""

    PENDING = "pending"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    
class BaseShipment(BaseModel):
    """Base shipment model."""
    content: Annotated[str, Field(..., description="Description of the shipment.")]
    status: Annotated[ShipmentStatusEnum, Field(
        default=ShipmentStatusEnum.PENDING,
        description="Current status of the shipment.",
    )]
    weight: Annotated[float, Field(..., description="Weight of the shipment.")]


class ShipmentBody(BaseShipment):
    """Request body for create / full-update endpoints."""
    weight: Annotated[
        float,
        Field(gt=0, lt=25, description="Weight of the shipment must be >0 and <25kg.")
    ] 


class ShipmentPatch(BaseModel):
    """Request body for partial-update (PATCH) endpoint."""
    content: Annotated[
        str | None, Field(default=None, description="Description of the shipment.")
    ] = None
    status: Annotated[
        ShipmentStatusEnum | None,
        Field(default=None, description="Current status of the shipment."),
    ] = None
    weight: Annotated[
        float | None,
        Field(
            default=None,
            gt=0,
            lt=25,
            description="Weight of the shipment must be >0 and <25kg.",
        ),
    ] = None 


class ShipmentStatus(BaseShipment):
    """Response body for Shipment endpoints."""
    id: Annotated[int, Field(..., description="Unique identifier of the shipment.")]