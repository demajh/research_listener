# Load env-vars for one-off test
export $(grep -v '^#' .env | xargs)

echo $GMAIL_USER
echo $GMAIL_APP_PASSWORD

python3 - <<'PY'
import os
from pathlib import Path
from utils.email_utils import send_email
send_email(
    to_email=os.getenv("GMAIL_USER"),
    subject="ArXiv-Listener test ✔",
    body_md="**Hello!**  Your Gmail SMTP setup works.",
    attachments=[Path("README.md")],   # any small file
)
PY
