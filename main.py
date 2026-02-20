from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import uuid
from datetime import datetime

from database import get_db, engine, Base
from schemas import (
    CampaignCreate, CampaignResponse,
    ReferralCreate, ReferralResponse,
    RewardCreate, RewardResponse,
    WebhookPayload, WidgetConfig
)
from crud import (
    create_campaign, get_campaign, get_campaigns,
    create_referral, get_referral, get_referrals_by_campaign,
    create_reward, get_rewards, update_reward_fulfillment
)

app = FastAPI(title="ReferralRewards API", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard for managing referral campaigns"""
    campaigns = get_campaigns(db)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "campaigns": campaigns
    })


# Campaign endpoints
@app.post("/api/campaigns", response_model=CampaignResponse)
def create_campaign_endpoint(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """Create a new referral campaign"""
    return create_campaign(db, campaign)

@app.get("/api/campaigns", response_model=List[CampaignResponse])
def list_campaigns(db: Session = Depends(get_db)):
    """List all referral campaigns"""
    return get_campaigns(db)

@app.get("/api/campaigns/{campaign_id}", response_model=CampaignResponse)
def get_campaign_endpoint(campaign_id: str, db: Session = Depends(get_db)):
    """Get campaign details"""
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


# Referral endpoints
@app.post("/api/referrals", response_model=ReferralResponse)
def create_referral_endpoint(referral: ReferralCreate, db: Session = Depends(get_db)):
    """Create a new referral record"""
    campaign = get_campaign(db, referral.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return create_referral(db, referral)

@app.get("/api/referrals/{referral_code}", response_model=ReferralResponse)
def get_referral_endpoint(referral_code: str, db: Session = Depends(get_db)):
    """Get referral by code"""
    referral = get_referral(db, referral_code)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    return referral

@app.get("/api/campaigns/{campaign_id}/referrals", response_model=List[ReferralResponse])
def get_campaign_referrals(campaign_id: str, db: Session = Depends(get_db)):
    """Get all referrals for a campaign"""
    return get_referrals_by_campaign(db, campaign_id)


# Reward endpoints
@app.post("/api/rewards", response_model=RewardResponse)
def create_reward_endpoint(reward: RewardCreate, db: Session = Depends(get_db)):
    """Create a reward for a referral"""
    return create_reward(db, reward)

@app.get("/api/referrals/{referral_id}/rewards", response_model=List[RewardResponse])
def get_referral_rewards(referral_id: str, db: Session = Depends(get_db)):
    """Get all rewards for a referral"""
    return get_rewards(db, referral_id)

@app.post("/api/rewards/{reward_id}/fulfill")
def fulfill_reward(reward_id: str, fulfillment_data: dict, db: Session = Depends(get_db)):
    """Mark a reward as fulfilled"""
    reward = update_reward_fulfillment(db, reward_id, fulfillment_data)
    if not reward:
        raise HTTPException(status_code=404, detail="Reward not found")
    return {"status": "fulfilled", "reward_id": reward_id}


# Webhook endpoint for tracking actions
@app.post("/api/webhooks/track")
def track_action(payload: WebhookPayload, db: Session = Depends(get_db)):
    """Webhook endpoint to track rewardable actions from external apps"""
    referral = get_referral(db, payload.referral_code)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    # Create reward for the action
    reward = create_reward(db, RewardCreate(
        referral_id=referral.id,
        action_type=payload.action_type,
        reward_type="credit",  # Default, can be customized
        reward_value=payload.metadata.get("reward_value", 10),
        status="pending"
    ))
    
    return {
        "status": "tracked",
        "referral_code": payload.referral_code,
        "action": payload.action_type,
        "reward_id": reward.id
    }


# Widget configuration endpoint
@app.get("/api/widget/{campaign_id}", response_model=WidgetConfig)
def get_widget_config(campaign_id: str, db: Session = Depends(get_db)):
    """Get widget configuration for embedding"""
    campaign = get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return WidgetConfig(
        campaign_id=campaign.id,
        campaign_name=campaign.name,
        reward_description=campaign.reward_description,
        primary_color="#6366f1",
        api_base_url="http://localhost:8000"
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)