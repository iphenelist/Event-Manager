# Event Manager — Frappe Custom App

A Frappe custom app for managing event invitations with:
- Personalized card generation (Pillow image composition)
- Unique QR codes per guest
- WhatsApp delivery (Fonnte / WaBlas / Custom)
- Guest download page
- Gate check-in QR scanner

---

## Installation

```bash
# 1. Navigate to your bench
cd /path/to/frappe-bench

# 2. Get the app
bench get-app event_manager /path/to/event_manager
# OR if hosted on git:
# bench get-app event_manager https://github.com/yourorg/event_manager

# 3. Install Python dependencies
cd apps/event_manager
pip install -r requirements.txt

# 4. Install on your site
bench --site yoursite.com install-app event_manager

# 5. Run migrations
bench --site yoursite.com migrate

# 6. Build assets
bench build --app event_manager

# 7. Restart
bench restart
```

---

## Configuration

### 1. Event Manager Settings
Go to: **Settings > Event Manager Settings**

- **WhatsApp Provider**: Choose Fonnte (recommended for Tanzania)
- **WhatsApp API URL**: `https://api.fonnte.com/send`
- **WhatsApp API Token**: Your Fonnte token
- **Sender Label**: e.g. `MN Printing`
- **Base URL**: Your site URL e.g. `https://yourdomain.com`
- **Name Color**: `#8B6914` (gold — matches most designs)
- **Card Type Color**: `#C8960C`
- **Name Font Size**: `36` (adjust based on your card design)

### 2. Get Fonnte Token
1. Register at https://fonnte.com
2. Connect your WhatsApp number
3. Copy your API token to settings

---

## Usage

### Creating an Event
1. Go to **Event Manager > Event > New**
2. Fill in event details (name, date, time, venue, dress code, contacts)
3. **Upload your Canva card design** as PNG/JPG
4. Add guests in the Guest table (name, phone, card type)
5. Save

### Generating Cards
- Click **Actions > Generate All Cards**
- System overlays each guest's name, card type, and unique QR code
- Cards saved as images in Frappe files

### Sending WhatsApp
- Click **Actions > Send All WhatsApp**
- Sends card image + Swahili text message to each guest
- Message includes download link, event details, contacts

### Guest Download Page
Each guest gets a unique link:
```
https://yourdomain.com/invitee/download/event-card/123456
```
Page shows:
- Their personalized card
- Download button
- View Location button
- Event details

### Gate Check-in
Staff opens on mobile:
```
https://yourdomain.com/gate-checkin
```
- Scans QR with phone camera
- ✅ Valid — new entry, shows guest name & card type
- ⚠️ Already Used — duplicate scan
- ❌ Invalid — not registered

---

## Card Composition Notes

The system auto-detects overlay positions as percentages of the card dimensions:
- **Guest Name**: 58% from left, 53% from top
- **Card Type**: below name
- **QR Code**: 68% from left, 72% from top, 20% of card width

For different card designs, you may need to adjust these values in:
`event_manager/utils/card_composer.py`

Look for the `# --- Positioning ---` section and adjust the percentages.

---

## File Structure

```
event_manager/
├── event_manager/
│   ├── doctype/
│   │   ├── event_manager_settings/   ← Global settings (Single)
│   │   ├── event/                    ← Event doctype
│   │   └── event_guest/              ← Guest child table
│   ├── utils/
│   │   ├── card_composer.py          ← Pillow image composition
│   │   ├── qr_generator.py           ← QR code generation
│   │   └── whatsapp_sender.py        ← WhatsApp API integration
│   └── www/
│       ├── invitee/download/event-card/  ← Guest download page
│       └── gate-checkin/                 ← Gate scanner page
├── requirements.txt
└── setup.py
```