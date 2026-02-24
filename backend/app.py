"""
Mailing service backend – send emails via Gmail SMTP.
"""
import html
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)

GMAIL_SMTP = "smtp.gmail.com"
GMAIL_PORT = 587


URL_RE = re.compile(r'(https?://[^\s<>&]+)')
BOLD_RE = re.compile(r'\*\*(.+?)\*\*')
ITALIC_RE = re.compile(r'\*(.+?)\*')


def _inline_format(escaped_text: str) -> str:
    """Apply inline formatting after HTML-escaping.

    Supported:
      **text**  → bold
      *text*    → italic
      URLs      → clickable links
    """
    text = BOLD_RE.sub(r'<strong>\1</strong>', escaped_text)
    text = ITALIC_RE.sub(r'<em>\1</em>', text)
    text = URL_RE.sub(r'<a href="\1" style="color:#6366f1;">\1</a>', text)
    return text


def body_to_html(text: str) -> str:
    """Convert plain text to HTML with formatting, line breaks and paragraphs."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    paragraphs = text.split("\n\n")
    html_parts = []
    for p in paragraphs:
        escaped = html.escape(p)
        escaped = _inline_format(escaped)
        escaped = escaped.replace("\n", "<br>\n")
        html_parts.append(f'<p style="margin:0 0 1em 0;">{escaped}</p>')

    return (
        '<div style="font-family: sans-serif; font-size: 14px; line-height: 1.6;">'
        + "\n".join(html_parts)
        + "</div>"
    )


def send_one(sender_email: str, app_password: str, to: str, subject: str, body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = to
    msg["Subject"] = subject
    # Plain-text fallback (for clients that don't render HTML)
    msg.attach(MIMEText(body, "plain"))
    # HTML version with explicit formatting
    msg.attach(MIMEText(body_to_html(body), "html"))
    with smtplib.SMTP(GMAIL_SMTP, GMAIL_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, to, msg.as_string())


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/send", methods=["POST"])
def send_emails():
    """
    Send one or more emails at once.
    Body: {
      "gmail": "your@gmail.com",
      "appPassword": "xxxx xxxx xxxx xxxx",
      "emails": [
        { "to": "recipient@example.com", "subject": "...", "body": "..." }
      ]
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    gmail = (data.get("gmail") or "").strip()
    app_password = (data.get("appPassword") or "").strip()
    emails = data.get("emails")

    if not gmail or not app_password:
        return jsonify({"error": "gmail and appPassword are required"}), 400
    if not emails or not isinstance(emails, list):
        return jsonify({"error": "emails must be a non-empty array"}), 400

    results = []
    for i, item in enumerate(emails):
        to = (item.get("to") or "").strip()
        subject = (item.get("subject") or "").strip()
        body = item.get("body") or ""
        if not to:
            results.append({"index": i, "to": to, "success": False, "error": "Missing 'to' address"})
            continue
        try:
            print(f"[DEBUG] body repr for {to}: {body!r}")
            send_one(gmail, app_password, to, subject, body)
            results.append({"index": i, "to": to, "success": True})
        except Exception as e:
            results.append({"index": i, "to": to, "success": False, "error": str(e)})

    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
