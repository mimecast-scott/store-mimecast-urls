import asyncio
import imaplib
import email
import re
import os
import time
import auth

import aiohttp
from pickledb import PickleDB

# === Configuration ===
IMAP_SERVER = os.getenv('IMAP_SERVER')
IMAP_USERNAME = os.getenv('IMAP_USERNAME')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')
IMAP_FOLDER = os.getenv('IMAP_FOLDER', 'Inbox')
DELAY = int(os.getenv('DELAY', 30))  # seconds between runs

# === Mimecast API ===
MIMECAST_API_URL = "https://api.services.mimecast.com/api/ttp/url/decode-url"
MIMECAST_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# === PickleDB ===
db = PickleDB('./data/mimecast_urls.json')

# === URL Regex ===
MIMECAST_URL_REGEX = r'https:\/\/[^\s")]+mimecastprotect\.com[^\s")]*'

def connect_to_imap():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(IMAP_USERNAME, IMAP_PASSWORD)
        mail.select(IMAP_FOLDER)
        print("✅ Connected to IMAP and selected folder:", IMAP_FOLDER)
        return mail
    except Exception as e:
        print("❌ IMAP connection failed:", e)
        return None

def extract_mimecast_urls(text: str):
    return re.findall(MIMECAST_URL_REGEX, text)

async def decode_url(session: aiohttp.ClientSession, url: str, token: str):
    payload = {"data": [{"url": url}]}
    # override/add auth header per request
    headers = {
        **MIMECAST_HEADERS,
        "Authorization": f"Bearer {token}"
    }
    try:
        async with session.post(MIMECAST_API_URL, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            body = await resp.json()
            data = body.get('data', [])
            if data:
                return data[0].get('url')
    except Exception as e:
        print(f"❌ Error decoding {url}: {e}")
    return None

async def process_email(session: aiohttp.ClientSession, mail, email_id: bytes, token: str):
    _, data = mail.fetch(email_id, '(BODY.PEEK[])')
    msg = email.message_from_bytes(data[0][1])
    urls = []
    for part in msg.walk():
        if part.get_content_type() in ['text/plain', 'text/html']:
            try:
                body = part.get_payload(decode=True).decode(errors='ignore')
                urls.extend(extract_mimecast_urls(body))
            except Exception as e:
                print(f"⚠️ Error decoding email part: {e}")

    found = False
    for url in urls:
        if not db.get(url):
            print(f"🔍 Found new URL: {url}")
            decoded = await decode_url(session, url, token)
            if decoded:
                db.set(url, decoded)
                print(f"✅ Stored: {url} → {decoded}")
                found = True
            else:
                print(f"❌ Could not decode: {url}")
        else:
            print(f"🗃️ Already stored: {url} → {db.get(url)}")
            found = True
    return found

async def fetch_and_process_emails(session: aiohttp.ClientSession, token: str):
    mail = connect_to_imap()
    if not mail:
        return

    _, data = mail.search(None, "UNSEEN")
    email_ids = data[0].split()
    print(f"📬 Found {len(email_ids)} unseen emails")

    for eid in email_ids:
        processed = await process_email(session, mail, eid, token)
        if processed:
            mail.store(eid, '+FLAGS', '(\\Seen)')

    mail.close()
    mail.logout()

async def main():
    # initial token retrieval (you may want to refresh periodically)
    token = auth.return_auth_key()

    # reuse one session for all decode calls
    async with aiohttp.ClientSession() as session:
        while True:
            await fetch_and_process_emails(session, token)
            db.save()
            print(f"⏳ Sleeping for {DELAY} seconds...\n")
            await asyncio.sleep(DELAY)

if __name__ == "__main__":
    asyncio.run(main())
