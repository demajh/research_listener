import os
import time
from datetime import datetime
from pathlib import Path

import schedule
from sqlalchemy.orm import Session

from db import SessionLocal
from models.user import Subscription
from utils.nlp_utils import fetch_latest, filter_articles, summarise_article
from utils.pdf_utils import md_to_pdf
from utils.email_utils import send_email

REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "./daily_reports"))
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def get_active_users(db: Session):
    return db.query(Subscription).filter(Subscription.is_active.is_(True)).all()

# ------------------------------------------------------------------ #
def generate_report(sub, relevant):
    summary_blocks = [summarise_article(p) for p in relevant]
    md = (
        f"# Daily arXiv digest for **{sub.interest_description}**  \n"
        f"*Channel:* `{sub.arxiv_channel}`  –  *Generated:* {datetime.utcnow():%d %b %Y %H:%M UTC*\n\n"
        + "\n\n".join(summary_blocks)
    )

    date_tag = datetime.utcnow().strftime("%Y%m%d")
    base_name = f"{sub.email.replace('@', '_')}_{date_tag}"
    md_path = REPORTS_DIR / f"{base_name}.md"
    pdf_path = md_path.with_suffix(".pdf")

    md_path.write_text(md, encoding="utf-8")
    md_to_pdf(md, pdf_path)

    return md, [md_path, pdf_path]

# ------------------------------------------------------------------ #
def daily_job():
    start = time.time()
    print(f"[{datetime.utcnow():%Y-%m-%d %H:%M}] Scheduler run start")

    db = SessionLocal()
    try:
        for sub in get_active_users(db):
            print(f" → {sub.email} | {sub.arxiv_channel}")

            papers = fetch_latest(sub.arxiv_channel, max_results=120)
            relevant = filter_articles(papers, sub.interest_description)
            if not relevant:
                print("   (no relevant papers today)")
                continue

            body_md, files = generate_report(sub, relevant)
            send_email(
                sub.email,
                subject=f"Your arXiv digest – {datetime.utcnow():%d %b %Y}",
                body_md=body_md,
                attachments=files,
            )
    finally:
        db.close()

    print(f"Run finished in {time.time() - start:.1f}s")

# ------------------------------------------------------------------ #
schedule_time = os.getenv("DAILY_RUN_UTC", "08:00")
schedule.every().day.at(schedule_time).do(daily_job)

if __name__ == "__main__":
    print("Scheduler waiting for", schedule_time, "UTC")
    while True:
        schedule.run_pending()
        time.sleep(60)
