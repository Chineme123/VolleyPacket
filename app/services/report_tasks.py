import os
import re

import pandas as pd

from app.services.jobs import Job
from app.services.brevo import get_successful_emails, parse_brevo_csv
from app import config


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def generate_report(job: Job, brevo_csv_path: str = None) -> str:
    # Source 1: All candidates from the job
    candidates = job.data.copy()
    candidates = candidates.fillna("")
    candidates["_email_key"] = candidates["Email"].astype(str).str.strip().str.lower()

    # Source 2: Local run log
    run_log = pd.DataFrame()
    if job.log_path and os.path.isfile(job.log_path):
        run_log = pd.read_csv(job.log_path)
        run_log = run_log.fillna("")
        run_log["_email_key"] = run_log["Email"].astype(str).str.strip().str.lower()

    # Source 3: Brevo delivery data
    if brevo_csv_path and os.path.isfile(brevo_csv_path):
        brevo_success = parse_brevo_csv(brevo_csv_path)
    else:
        brevo_success = get_successful_emails()

    # Sheet 1: Sent
    sent = candidates[candidates["_email_key"].isin(brevo_success)].copy()

    # Sheet 2: Missing
    missing = candidates[~candidates["_email_key"].isin(brevo_success)].copy()

    # Sheet 3: Bad Emails
    is_bad = ~candidates["_email_key"].apply(lambda e: bool(EMAIL_RE.match(e)))
    bad_emails = candidates[is_bad].copy()
    bad_emails["Reason"] = "Invalid email format"

    # Sheet 4: Failed Locally
    failed_locally = pd.DataFrame()
    if not run_log.empty:
        pdf_ok = run_log[run_log["PDFGenerated"].astype(str).str.strip().str.lower() == "true"]
        not_delivered = pdf_ok[~pdf_ok["_email_key"].isin(brevo_success)]
        if not not_delivered.empty:
            deduped = not_delivered.sort_index().drop_duplicates(subset="_email_key", keep="last")
            error_map = deduped.set_index("_email_key")["Error"]
            failed_locally = candidates[candidates["_email_key"].isin(deduped["_email_key"])].copy()
            failed_locally["Error"] = failed_locally["_email_key"].map(error_map).fillna("")

    # Write
    drop_key = lambda df: df.drop(columns=["_email_key"], errors="ignore")
    os.makedirs(config.LOG_FOLDER, exist_ok=True)
    report_path = os.path.join(config.LOG_FOLDER, f"report_{job.job_id}.xlsx")

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        drop_key(sent).to_excel(writer, sheet_name="Sent", index=False)
        drop_key(missing).to_excel(writer, sheet_name="Missing", index=False)
        drop_key(bad_emails).to_excel(writer, sheet_name="Bad Emails", index=False)
        drop_key(failed_locally).to_excel(writer, sheet_name="Failed Locally", index=False)

    return report_path
