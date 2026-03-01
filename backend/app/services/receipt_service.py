"""
receipt_service.py — BenefitReceipt HTML generator + S3 uploader.

Generates a human-readable HTML eligibility receipt with:
  - Scheme name + verdict
  - Eligibility rules trace (what passed / failed)
  - Document checklist (from schemes_config.yaml)
  - Case ID + official links
  - Presigned S3 URL (7-day expiry) or local fallback JSON

Design: deterministic output — no LLM involved.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

RECEIPT_BUCKET   = os.getenv("RECEIPT_BUCKET", "jansathi-receipts")
RECEIPT_BASE_URL = os.getenv("RECEIPT_BASE_URL", "https://jansathi.example.com/receipt")

# ── Document checklists per scheme (supplement YAML with standard docs) ───────
STANDARD_DOCS = {
    "pm_kisan": [
        "Aadhaar Card (original + photocopy)",
        "Land records / Khatoni (revenue document showing < 2 hectares)",
        "Bank passbook (first page with IFSC + account number)",
        "Mobile number linked to Aadhaar",
    ],
    "pm_awas_urban": [
        "Aadhaar Card",
        "Income Certificate (from Tehsildar / competent authority)",
        "Self-declaration: no pucca house",
        "Bank passbook",
        "Passport-size photograph",
    ],
    "e_shram": [
        "Aadhaar Card",
        "Mobile number linked to Aadhaar",
        "Bank account (for DBT)",
    ],
}

OFFICIAL_LINKS = {
    "pm_kisan":        "https://pmkisan.gov.in",
    "pm_awas_urban":   "https://pmaymis.gov.in",
    "e_shram":         "https://eshram.gov.in",
}


class ReceiptService:
    """Generates BenefitReceipt HTML pages and uploads to S3."""

    def generate_receipt(
        self,
        session_id: str,
        scheme_name: str,
        eligible: bool,
        rules_trace: list,
        rules_score: float,
        slots: dict,
        case_id: Optional[str] = None,
        language: str = "hi",
    ) -> dict:
        """
        Generate receipt and upload to S3.

        Returns:
          {
            "case_id": str,
            "receipt_url": str,           # presigned or fallback URL
            "receipt_html": str,          # HTML string (for inline render)
            "document_checklist": list,   # required docs
            "scheme_name": str,
            "eligible": bool,
            "rules_score": float,
          }
        """
        case_id = case_id or f"JS-{datetime.now(timezone.utc).strftime('%Y-%m')}-{uuid.uuid4().hex[:6].upper()}"
        checklist = self.generate_document_checklist(scheme_name)
        display_name = self._scheme_display_name(scheme_name)
        official_link = OFFICIAL_LINKS.get(scheme_name, "https://india.gov.in")
        generated_at  = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")

        verdict_emoji = "✅" if eligible else "❌"
        verdict_text  = "ELIGIBLE" if eligible else "NOT ELIGIBLE"
        verdict_color = "#16a34a" if eligible else "#dc2626"

        # Build rules rows — handles both dict (new) and string (legacy) entries
        def _rule_row(r):
            if isinstance(r, dict):
                icon = "✅" if r.get("pass") else "❌"
                label = r.get("label", r.get("rule", ""))
                user_val = r.get("user_value", "")
                req_val = r.get("required_value", "")
                detail = f" (yours: {user_val}, required: {req_val})" if user_val is not None else ""
                return f"<tr><td style='padding:8px 12px;border-bottom:1px solid #e5e7eb'>{icon} {label}{detail}</td></tr>"
            return f"<tr><td style='padding:8px 12px;border-bottom:1px solid #e5e7eb'>{r}</td></tr>"

        rules_rows = "".join(_rule_row(r) for r in rules_trace)

        # Build checklist items
        checklist_items = "".join(
            f"<li style='margin:6px 0;'>📄 {doc}</li>"
            for doc in checklist
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>JanSathi BenefitReceipt — {case_id}</title>
  <style>
    body{{font-family:'Segoe UI',Arial,sans-serif;background:#f9fafb;margin:0;padding:0}}
    .container{{max-width:640px;margin:32px auto;background:#fff;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,.08);overflow:hidden}}
    .header{{background:#16a085;color:#fff;padding:28px 32px}}
    .header h1{{margin:0;font-size:24px;font-weight:700;letter-spacing:-.5px}}
    .header p{{margin:6px 0 0;opacity:.85;font-size:14px}}
    .verdict{{display:flex;align-items:center;gap:12px;padding:24px 32px;background:{verdict_color}10;border-left:6px solid {verdict_color}}}
    .verdict-badge{{font-size:28px}}
    .verdict-title{{font-size:20px;font-weight:700;color:{verdict_color}}}
    .verdict-score{{font-size:13px;color:#6b7280}}
    section{{padding:20px 32px;border-bottom:1px solid #f3f4f6}}
    h3{{margin:0 0 12px;font-size:14px;text-transform:uppercase;letter-spacing:1px;color:#6b7280}}
    table{{width:100%;border-collapse:collapse;font-size:14px}}
    .checklist{{list-style:none;padding:0;margin:0;font-size:14px}}
    .cta{{padding:24px 32px;display:flex;gap:12px;flex-wrap:wrap}}
    .btn{{display:inline-block;padding:12px 24px;border-radius:8px;font-size:14px;font-weight:600;text-decoration:none;cursor:pointer}}
    .btn-primary{{background:{verdict_color};color:#fff}}
    .btn-secondary{{background:#f3f4f6;color:#374151}}
    .footer{{padding:16px 32px;font-size:12px;color:#9ca3af;text-align:center}}
    @media print{{.cta{{display:none}}}}
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🏛️ JanSathi BenefitReceipt</h1>
    <p>Case ID: <strong>{case_id}</strong> &nbsp;|&nbsp; Generated: {generated_at}</p>
  </div>

  <div class="verdict">
    <div class="verdict-badge">{verdict_emoji}</div>
    <div>
      <div class="verdict-title">{verdict_text}</div>
      <div class="verdict-score">{display_name} &nbsp;·&nbsp; Confidence: {int(rules_score*100)}%</div>
    </div>
  </div>

  <section>
    <h3>Eligibility Rules Trace</h3>
    <table><tbody>{rules_rows}</tbody></table>
  </section>

  <section>
    <h3>Required Documents Checklist</h3>
    <ul class="checklist">{checklist_items}</ul>
  </section>

  <section>
    <h3>Next Steps</h3>
    <p style="font-size:14px;color:#374151;margin:0">
      {"✅ You appear eligible. Visit your nearest CSC center or apply online with the documents listed above." if eligible else "❌ Based on current information, you may not meet all eligibility criteria. Visit your nearest CSC for alternative schemes."}
    </p>
    <p style="font-size:13px;color:#6b7280;margin-top:8px">
      Official portal: <a href="{official_link}" style="color:#16a085">{official_link}</a>
    </p>
  </section>

  <div class="cta">
    <a href="{official_link}" class="btn btn-primary" target="_blank">Apply on Official Portal →</a>
    <a href="#" onclick="window.print()" class="btn btn-secondary">Print / Save PDF</a>
  </div>

  <div class="footer">
    JanSathi is a civic readiness tool. This receipt is advisory only.<br/>
    It does not guarantee scheme approval. Official decisions rest with the Government of India.
  </div>
</div>
</body>
</html>"""

        # Upload to S3
        receipt_url = self._upload_to_s3(case_id, html)

        logger.info(f"[ReceiptService] Generated receipt for case={case_id} scheme={scheme_name} eligible={eligible}")

        return {
            "case_id": case_id,
            "receipt_url": receipt_url,
            "receipt_html": html,
            "document_checklist": checklist,
            "scheme_name": display_name,
            "eligible": eligible,
            "rules_score": round(rules_score, 3),
        }

    def generate_document_checklist(self, scheme_name: str) -> list:
        """Return document checklist for a given scheme."""
        # First check YAML config for any extra docs, then standard list
        docs = list(STANDARD_DOCS.get(scheme_name, []))
        try:
            import yaml
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "schemes_config.yaml"
            )
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            extra = config.get("schemes", {}).get(scheme_name, {}).get("documents", [])
            for d in extra:
                if d not in docs:
                    docs.append(d)
        except Exception:
            pass
        return docs if docs else [
            "Aadhaar Card",
            "Proof of residence",
            "Bank passbook",
        ]

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _upload_to_s3(self, case_id: str, html: str) -> str:
        key = f"receipts/{case_id}.html"
        try:
            import boto3
            from botocore.config import Config
            region = os.getenv("AWS_REGION", "ap-south-1")
            s3 = boto3.client("s3", region_name=region, config=Config(signature_version="s3v4"))
            s3.put_object(
                Bucket=RECEIPT_BUCKET,
                Key=key,
                Body=html.encode("utf-8"),
                ContentType="text/html; charset=utf-8",
            )
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": RECEIPT_BUCKET, "Key": key},
                ExpiresIn=604800,   # 7 days
            )
            return url
        except Exception as e:
            logger.warning(f"[ReceiptService] S3 upload failed (using fallback): {e}")
            return f"{RECEIPT_BASE_URL}/{case_id}"

    def _scheme_display_name(self, scheme_name: str) -> str:
        names = {
            "pm_kisan":      "PM-Kisan Samman Nidhi",
            "pm_awas_urban": "PM Awas Yojana (Urban)",
            "e_shram":       "E-Shram Registration",
        }
        return names.get(scheme_name, scheme_name.replace("_", " ").title())
