from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal

app = FastAPI()

# the only class that 'log-generator' can manage
class AlertCreate(BaseModel):
    ip_source:str
    event_type:str
    message:str
    score:float
    is_malicious: bool

class Alert(BaseModel):
    id:int
    status: Literal["PENDING", "TRUE_POSITIVE", "FALSE_POSITIVE"]
    ip_source:str
    event_type:str
    message:str
    score:float
    is_malicious: bool

class StatusUpdate(BaseModel): 
    value: Literal["PENDING", "TRUE_POSITIVE", "FALSE_POSITIVE"]

# temporary stockage
temporary = []

@app.get("/")
def read_root():
    return f" Hello World =^..^= "

@app.post("/alerts")
def add_alert(alertCreate:AlertCreate):
    # converts the AlertCreate object into an Alert object
    alert = Alert(id=len(temporary) + 1,
                  status="PENDING",
                  ip_source=alertCreate.ip_source,
                  event_type=alertCreate.event_type,
                  message=alertCreate.message,
                  score=alertCreate.score,
                  is_malicious=alertCreate.is_malicious)
    # add the new alert to the temporary list
    temporary.append(alert)

    return

@app.patch("/alerts/{id}")
def patch_status(id:int, statusUpdate:StatusUpdate):
    # boolean to track if we found the alert
    found = False
    # searching for the alert with the associated id
    for items in temporary:
        if items.id == id:
            items.status = statusUpdate.value
            found = True
            break

    # raise an error if we didnt find the alert
    if not found:
        raise HTTPException(404, "The alert was not found")
    return {"status": "updated", "id": id, "new_status": statusUpdate.value}
    

@app.get("/alerts")
def read_items():
    return temporary