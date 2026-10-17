from pydantic import BaseModel
from typing import List, Optional

class Merchant(BaseModel):
    id: str
    category_code: int

class Device(BaseModel):
    device_fingerprint: str
    ip_address: str
    user_agent: str

class Location(BaseModel):
    latitude: float
    longitude: float

class TransactionRequest(BaseModel):
    transaction_id: str
    account_id: str
    merchant: Merchant
    amount: float
    currency: str ="INR"
    timestamp: str
    device: Device
    location: Location

class TransactionResponse(BaseModel):
    eval_id: str
    transaction_id: str
    risk_score: float
    verdict: str
    latency_ms: float
    reasons: List[str]
    challenge_details: Optional[dict] = None