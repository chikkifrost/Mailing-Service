# Mailing Service

Add your Gmail, write one message, and send it to many recipients at once.

## Setup

### 1. Gmail App Password

Gmail requires an **App Password** for SMTP (your normal password will not work).

1. Go to [Google Account → Security](https://myaccount.google.com/security).
2. Turn on **2-Step Verification** if it’s not already on.
3. Open [App passwords](https://myaccount.google.com/apppasswords).
4. Create an app password for “Mail” (or “Other”) and copy the 16-character password (e.g. `xxxx xxxx xxxx xxxx`).

### 2. Install and run

From the project root:

```bash
pip install -r requirements.txt
python backend/app.py
```

Then open **http://localhost:5050** in your browser.

### 3. Use the app

1. **Gmail account** – Enter your Gmail address and the App Password from step 1.
2. **Email content** – Enter subject and body (HTML is supported). Same content is sent to everyone.
3. **Recipients** – Add one email address per line.
4. Click **Send all at once** to send the same email to every recipient.

Credentials are only used for the request; they are not stored anywhere.

## Project layout

- `backend/app.py` – Flask server and Gmail SMTP sending.
- `frontend/` – Static UI (HTML, CSS, JS) served at `/`.
# Mailing-Service
