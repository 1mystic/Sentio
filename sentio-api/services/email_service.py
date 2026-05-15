"""
Email delivery via Resend (free tier: 3,000/month, 100/day).
Set RESEND_API_KEY and RESEND_FROM_EMAIL in .env.
If key is absent, emails are logged only (no send).
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "noreply@sentio.app")
APP_URL = os.getenv("APP_URL", "https://sentio.app")


async def send_email(to: str, subject: str, html: str) -> bool:
    if not RESEND_API_KEY:
        logger.info(f"[EMAIL-STUB] To={to} | Subject={subject}")
        return True
    try:
        async with httpx.AsyncClient() as http:
            res = await http.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
                json={"from": FROM_EMAIL, "to": [to], "subject": subject, "html": html},
                timeout=10,
            )
            if res.status_code in (200, 201):
                return True
            logger.warning(f"Resend error {res.status_code}: {res.text}")
            return False
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False


def _base_template(content: str) -> str:
    return f"""
    <div style="font-family:'Helvetica Neue',sans-serif;max-width:560px;margin:0 auto;padding:32px 24px;background:#f4f3f8;">
      <div style="background:white;border-radius:16px;padding:32px;box-shadow:0 4px 24px rgba(53,43,56,0.07);">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:28px;">
          <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#dad8f9,#9b94e8);display:inline-flex;align-items:center;justify-content:center;font-size:18px;font-weight:900;color:#352b38;">S</div>
          <span style="font-size:20px;font-weight:800;color:#352b38;letter-spacing:-0.5px;">Sentio</span>
        </div>
        {content}
        <hr style="border:none;border-top:1px solid #eceaf9;margin:28px 0;" />
        <p style="font-size:12px;color:#7e808c;line-height:1.5;">
          You're receiving this because you have notifications enabled in your Sentio profile.
          <a href="{APP_URL}/profile" style="color:#9b94e8;">Manage preferences</a>
        </p>
      </div>
    </div>
    """


async def send_daily_reminder(to: str, user_name: str, streak: int) -> bool:
    streak_text = f"🔥 {streak}-day streak" if streak > 1 else "Start your streak today"
    html = _base_template(f"""
        <h2 style="font-size:22px;font-weight:700;color:#352b38;margin:0 0 8px;">Time to reflect, {user_name} ✍️</h2>
        <p style="color:#7e808c;font-size:15px;line-height:1.6;margin:0 0 20px;">
          A few minutes of journaling surfaces patterns you'd otherwise miss. Your thinking is worth examining.
        </p>
        <div style="background:#eceaf9;border-radius:12px;padding:16px;margin-bottom:24px;text-align:center;">
          <span style="font-size:18px;font-weight:800;color:#352b38;">{streak_text}</span>
        </div>
        <a href="{APP_URL}/journal/new"
           style="display:inline-block;background:#352b38;color:white;font-weight:600;font-size:14px;
                  padding:12px 28px;border-radius:10px;text-decoration:none;">
          Write Today's Entry →
        </a>
    """)
    return await send_email(to, f"Your daily reflection — Sentio", html)


async def send_weekly_digest(to: str, user_name: str, insights: list[dict], archetype: str | None) -> bool:
    insight_html = "".join(
        f'<li style="margin-bottom:8px;color:#7e808c;font-size:14px;line-height:1.6;">{i["text"]}</li>'
        for i in insights[:3]
    ) or '<li style="color:#7e808c;">Write more journal entries this week to unlock insights.</li>'

    archetype_block = (
        f'<div style="background:linear-gradient(135deg,#dad8f9,#eceaf9);border-radius:12px;padding:16px;margin-bottom:20px;">'
        f'<div style="font-size:12px;font-weight:600;color:#9b94e8;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:4px;">Your Cognitive Archetype</div>'
        f'<div style="font-size:18px;font-weight:800;color:#352b38;">{archetype}</div>'
        f'</div>'
    ) if archetype else ""

    html = _base_template(f"""
        <h2 style="font-size:22px;font-weight:700;color:#352b38;margin:0 0 8px;">Your weekly cognitive digest 🧠</h2>
        <p style="color:#7e808c;font-size:14px;margin:0 0 20px;">Here's what your thinking patterns looked like this week, {user_name}.</p>
        {archetype_block}
        <div style="margin-bottom:24px;">
          <div style="font-size:14px;font-weight:700;color:#352b38;margin-bottom:10px;">This week's insights</div>
          <ul style="margin:0;padding-left:20px;">{insight_html}</ul>
        </div>
        <a href="{APP_URL}/dashboard"
           style="display:inline-block;background:#9b94e8;color:#352b38;font-weight:700;font-size:14px;
                  padding:12px 28px;border-radius:10px;text-decoration:none;">
          View Full Dashboard →
        </a>
    """)
    return await send_email(to, f"Your Sentio weekly digest", html)


async def send_assessment_complete(to: str, user_name: str, assessment_title: str, score: int, archetype: str | None) -> bool:
    html = _base_template(f"""
        <h2 style="font-size:22px;font-weight:700;color:#352b38;margin:0 0 8px;">Assessment complete! 🎉</h2>
        <p style="color:#7e808c;font-size:14px;margin:0 0 20px;">Well done, {user_name}. Here's what we found.</p>
        <div style="background:#eceaf9;border-radius:12px;padding:20px;margin-bottom:24px;text-align:center;">
          <div style="font-size:13px;color:#9b94e8;font-weight:600;margin-bottom:4px;">{assessment_title}</div>
          <div style="font-size:36px;font-weight:800;color:#352b38;">{score}</div>
          <div style="font-size:12px;color:#7e808c;">Overall Score</div>
        </div>
        {"<p style='color:#352b38;font-weight:600;'>Your archetype: " + archetype + "</p>" if archetype else ""}
        <a href="{APP_URL}/assessments"
           style="display:inline-block;background:#352b38;color:white;font-weight:600;font-size:14px;
                  padding:12px 28px;border-radius:10px;text-decoration:none;">
          View Results →
        </a>
    """)
    return await send_email(to, f"Results: {assessment_title} — Sentio", html)

async def send_booking_notification(to: str, user_name: str, therapist_name: str) -> bool:
    html = _base_template(f"""
        <h2 style="font-size:22px;font-weight:700;color:#352b38;margin:0 0 8px;">Connection request sent! 🤝</h2>
        <p style="color:#7e808c;font-size:14px;margin:0 0 20px;">Hi {user_name}, we've received your request to connect with {therapist_name}.</p>
        <p style="color:#7e808c;font-size:14px;margin:0 0 20px;">They will review your request and get back to you soon.</p>
        <a href="{APP_URL}/therapists"
           style="display:inline-block;background:#352b38;color:white;font-weight:600;font-size:14px;
                  padding:12px 28px;border-radius:10px;text-decoration:none;">
          View directory →
        </a>
    """)
    return await send_email(to, f"Connection request sent to {therapist_name} — Sentio", html)

