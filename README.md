# 🎁 ReferralRewards

**Plug-and-play viral referral rewards for SaaS**

Add viral referral loops to your SaaS product in minutes, not months.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export WEBHOOK_SECRET="your-secure-random-secret-key"
```

**⚠️ Security Note:** The `WEBHOOK_SECRET` is used to verify webhook signatures and prevent unauthorized reward creation. Use a strong, random secret in production.

### 3. Run the API

```bash
python main.py
```

The API will start at `http://localhost:8000`

### 4. Open Dashboard

Visit `http://localhost:8000` to access the admin dashboard.

## 📋 API Endpoints

### Campaigns
- `POST /api/campaigns` - Create a referral campaign
- `GET /api/campaigns` - List all campaigns
- `GET /api/campaigns/{id}` - Get campaign details

### Referrals
- `POST /api/referrals` - Create a referral (generates unique code)
- `GET /api/referrals/{code}` - Get referral by code
- `GET /api/campaigns/{id}/referrals` - Get referrals for campaign

### Rewards
- `POST /api/rewards` - Create a reward for an action
- `GET /api/referrals/{id}/rewards` - Get rewards for referral
- `POST /api/rewards/{id}/fulfill` - Mark reward as fulfilled

### Webhooks
- `POST /api/webhooks/track` - Track rewardable actions from your app **(requires signature)**

### Widget
- `GET /api/widget/{campaign_id}` - Get widget configuration

## 🎨 Embedding the Widget

Add this script tag to your app:

```html
<script src="http://localhost:8000/static/widget.js" 
        data-campaign="YOUR_CAMPAIGN_ID"
        data-referrer="user@example.com">
</script>
```

## 📊 Dashboard Features

- Create and manage referral campaigns
- Copy-paste ready widget code
- View referral stats (clicks, conversions, rewards)

## 🔧 Example Usage

### 1. Create a Campaign

```bash
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{"name": "Summer Promo", "reward_description": "$50 credit per referral"}'
```

Response:
```json
{
  "id": "abc123",
  "name": "Summer Promo",
  "reward_description": "$50 credit per referral"
}
```

### 2. Create a Referral

```bash
curl -X POST http://localhost:8000/api/referrals \
  -H "Content-Type: application/json" \
  -d '{"campaign_id": "abc123", "referrer_email": "user@example.com"}'
```

Response:
```json
{
  "id": "ref456",
  "referral_code": "ABC123XY",
  "referrer_email": "user@example.com"
}
```

### 3. Track Actions via Webhook

When someone completes an action (signup, purchase, etc.), send a webhook with an HMAC-SHA256 signature:

```bash
# First, compute the signature (example in Python):
# import hmac, hashlib, json
# payload = json.dumps({"referral_code": "ABC123XY", "action_type": "signup", "metadata": {"reward_value": 50}})
# signature = hmac.new(b"your-secret-key", payload.encode(), hashlib.sha256).hexdigest()

curl -X POST http://localhost:8000/api/webhooks/track \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: YOUR_COMPUTED_SIGNATURE" \
  -d '{
    "referral_code": "ABC123XY",
    "action_type": "signup",
    "metadata": {"reward_value": 50}
  }'
```

**Webhook Signature Verification:**

The `/api/webhooks/track` endpoint requires an `X-Webhook-Signature` header containing an HMAC-SHA256 hash of the request body.

**How to generate the signature:**

```python
import hmac
import hashlib
import json

# Your webhook secret (same as WEBHOOK_SECRET env variable)
secret = "your-secure-random-secret-key"

# The JSON payload as a string
payload = json.dumps({
    "referral_code": "ABC123XY",
    "action_type": "signup",
    "metadata": {"reward_value": 50}
})

# Compute HMAC-SHA256 signature
signature = hmac.new(
    secret.encode('utf-8'),
    payload.encode('utf-8'),
    hashlib.sha256
).hexdigest()

print(f"X-Webhook-Signature: {signature}")
```

```javascript
// Node.js example
const crypto = require('crypto');

const secret = 'your-secure-random-secret-key';
const payload = JSON.stringify({
  referral_code: 'ABC123XY',
  action_type: 'signup',
  metadata: { reward_value: 50 }
});

const signature = crypto
  .createHmac('sha256', secret)
  .update(payload)
  .digest('hex');

console.log(`X-Webhook-Signature: ${signature}`);
```

### 4. Fulfill Rewards

When you're ready to give the reward:

```bash
curl -X POST http://localhost:8000/api/rewards/REWARD_ID/fulfill \
  -H "Content-Type: application/json" \
  -d '{"coupon_code": "SAVE50", "expires": "2024-12-31"}'
```

## 🏗️ Architecture

- **FastAPI** - Modern, fast web framework
- **SQLite** - Simple file-based database (easy to swap for PostgreSQL)
- **SQLAlchemy** - ORM for database operations
- **Jinja2** - Template engine for dashboard
- **Vanilla JS** - Lightweight widget (no framework dependencies)

## 🔒 Security

- **Webhook Signature Verification**: All webhook requests must include a valid HMAC-SHA256 signature to prevent unauthorized reward creation
- **Environment Variables**: Sensitive configuration (like `WEBHOOK_SECRET`) should be stored in environment variables
- **Production Recommendations**:
  - Use a cryptographically secure random string for `WEBHOOK_SECRET`
  - Use HTTPS in production
  - Consider rate limiting on webhook endpoints
  - Rotate secrets periodically

## 📝 License

MIT
