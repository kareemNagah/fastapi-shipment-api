from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status ,Response
from scalar_fastapi import get_scalar_api_reference

from .database import DataBase
from .schemas import ShipmentBody, ShipmentPatch, ShipmentStatus

load_dotenv()

app = FastAPI()
db = DataBase()


@app.post(
    "/shipment", status_code=status.HTTP_201_CREATED, response_model=ShipmentStatus
)
def create_shipment(body: ShipmentBody) -> ShipmentStatus:
    db.create(body)
    return db.get_latest()


@app.put(
    "/shipment/{id}", status_code=status.HTTP_200_OK, response_model=ShipmentStatus
)
def shipment_update(id: int, body: ShipmentBody) -> ShipmentStatus:

    replaced = db.replace(id, ShipmentBody.model_validate(body))

    if not replaced:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given shipment ID is not found!",
        )
    return replaced


@app.patch(
    "/shipment/{id}", status_code=status.HTTP_200_OK, response_model=ShipmentStatus
)
def patch_shipment(id: int, body: ShipmentPatch) -> ShipmentStatus:

    updated = db.update(id, ShipmentPatch.model_validate(body))

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given shipment ID is not found!",
        )
    return updated

@app.get("/shipment/latest", response_model=ShipmentStatus)
def get_latest_shipment() -> ShipmentStatus:
    latest_shipment = db.get_latest()
    return latest_shipment

@app.get("/shipment/{id}", response_model=ShipmentStatus)
def get_shipment(id: int) -> ShipmentStatus | None:
    shipment = db.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given shipment ID is not found!",
        )
    return shipment
 

@app.delete("/shipment/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shipment(id: int):
    deleted = db.delete(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given shipment ID is not found!",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scaler API",
        scalar_proxy_url="https://proxy.scalar.com",
    )
