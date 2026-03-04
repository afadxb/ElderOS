"""Stub PDF generation service.

Returns simple HTML encoded as bytes. In production, replace with
WeasyPrint + Jinja2 templates for proper PDF output.
"""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.incident import Incident
from src.services.report_service import get_board_report_data, get_shift_summaries
from src.utils.time_utils import dt_to_iso


async def generate_incident_pdf(
    db: AsyncSession, incident_id: str
) -> bytes | None:
    """Generate an incident report as HTML bytes (stub).

    Returns None if the incident is not found.
    """
    incident = await db.get(Incident, incident_id)
    if not incident:
        return None

    html = f"""<!DOCTYPE html>
<html>
<head><title>Incident Report - {incident.id}</title></head>
<body>
<h1>Incident Report</h1>
<table>
<tr><td><strong>Incident ID:</strong></td><td>{incident.id}</td></tr>
<tr><td><strong>Event ID:</strong></td><td>{incident.event_id}</td></tr>
<tr><td><strong>Room:</strong></td><td>{incident.room_number or "N/A"}</td></tr>
<tr><td><strong>Resident:</strong></td><td>{incident.resident_name or "N/A"}</td></tr>
<tr><td><strong>Event Type:</strong></td><td>{incident.event_type or "N/A"}</td></tr>
<tr><td><strong>Confidence:</strong></td><td>{incident.confidence or "N/A"} ({incident.confidence_score or 0}%)</td></tr>
<tr><td><strong>Status:</strong></td><td>{incident.status or "N/A"}</td></tr>
<tr><td><strong>Detected At:</strong></td><td>{dt_to_iso(incident.detected_at)}</td></tr>
<tr><td><strong>Acknowledged At:</strong></td><td>{dt_to_iso(incident.acknowledged_at) or "N/A"}</td></tr>
<tr><td><strong>Resolved At:</strong></td><td>{dt_to_iso(incident.resolved_at) or "N/A"}</td></tr>
<tr><td><strong>Ack Response (s):</strong></td><td>{incident.ack_response_seconds or "N/A"}</td></tr>
<tr><td><strong>Resolve Response (s):</strong></td><td>{incident.resolve_response_seconds or "N/A"}</td></tr>
<tr><td><strong>Acknowledged By:</strong></td><td>{incident.acknowledged_by or "N/A"}</td></tr>
<tr><td><strong>Resolved By:</strong></td><td>{incident.resolved_by or "N/A"}</td></tr>
<tr><td><strong>Unit:</strong></td><td>{incident.unit or "N/A"}</td></tr>
<tr><td><strong>Sensor Source:</strong></td><td>{incident.sensor_source or "N/A"}</td></tr>
<tr><td><strong>Repeat Fall:</strong></td><td>{"Yes" if incident.is_repeat_fall else "No"}</td></tr>
</table>

<h2>Pre-Event Summary</h2>
<p>{incident.pre_event_summary or "None recorded."}</p>

<h2>Post-Event State</h2>
<p>{incident.post_event_state or "None recorded."}</p>

<h2>Notes</h2>
<p>{incident.notes or "No notes."}</p>

<hr>
<p><em>Generated {dt_to_iso(datetime.now(timezone.utc))} by ElderOS</em></p>
</body>
</html>"""

    return html.encode("utf-8")


async def generate_board_report_pdf(db: AsyncSession) -> bytes:
    """Generate a board report as HTML bytes (stub)."""
    data = await get_board_report_data(db)

    unit_rows = ""
    for u in data["unit_summaries"]:
        unit_rows += (
            f"<tr>"
            f"<td>{u['unit']}</td>"
            f"<td>{u['falls']}</td>"
            f"<td>{u['avg_response_time']}s</td>"
            f"<td>{u['unwitnessed_rate'] * 100:.0f}%</td>"
            f"<td>{u['compliance_score']}%</td>"
            f"</tr>"
        )

    liability = data["liability_indicators"]
    trend_rows = ""
    for t in data["trends_monthly"]:
        trend_rows += (
            f"<tr>"
            f"<td>{t['month']}</td>"
            f"<td>{t['falls']}</td>"
            f"<td>{t['avg_response_time']}s</td>"
            f"</tr>"
        )

    html = f"""<!DOCTYPE html>
<html>
<head><title>Board Report - {data['period']}</title></head>
<body>
<h1>Board Report</h1>
<p><strong>Facility:</strong> {data['facility_name']}</p>
<p><strong>Period:</strong> {data['period']}</p>

<h2>Unit Summaries</h2>
<table border="1" cellpadding="4">
<tr><th>Unit</th><th>Falls</th><th>Avg Response</th><th>Unwitnessed Rate</th><th>Compliance</th></tr>
{unit_rows}
</table>

<h2>Liability Indicators</h2>
<ul>
<li>Slow responses (>3 min): {liability['slow_responses']}</li>
<li>Unacknowledged alerts: {liability['unacknowledged_alerts']}</li>
<li>Repeat falls: {liability['repeat_falls']}</li>
</ul>

<h2>Monthly Trends</h2>
<table border="1" cellpadding="4">
<tr><th>Month</th><th>Falls</th><th>Avg Response</th></tr>
{trend_rows}
</table>

<hr>
<p><em>Generated {dt_to_iso(datetime.now(timezone.utc))} by ElderOS</em></p>
</body>
</html>"""

    return html.encode("utf-8")


async def generate_shift_summary_pdf(
    db: AsyncSession, shift_id: str
) -> bytes:
    """Generate a shift summary as HTML bytes (stub).

    Since shift summaries are computed on the fly, this generates today's
    summaries and returns the full set. The shift_id parameter is informational.
    """
    summaries = await get_shift_summaries(db)

    summary_sections = ""
    for s in summaries:
        summary_sections += f"""
<h2>{s['shift_name']} Shift - {s['date']}</h2>
<table border="1" cellpadding="4">
<tr><td><strong>Unit:</strong></td><td>{s['unit']}</td></tr>
<tr><td><strong>Total Events:</strong></td><td>{s['total_events']}</td></tr>
<tr><td><strong>Falls:</strong></td><td>{s['falls']}</td></tr>
<tr><td><strong>Bed Exits:</strong></td><td>{s['bed_exits']}</td></tr>
<tr><td><strong>Inactivity Alerts:</strong></td><td>{s['inactivity_alerts']}</td></tr>
<tr><td><strong>Unsafe Transfers:</strong></td><td>{s['unsafe_transfers']}</td></tr>
<tr><td><strong>Avg Ack Time:</strong></td><td>{s['avg_ack_time_seconds']}s</td></tr>
<tr><td><strong>Avg Resolve Time:</strong></td><td>{s['avg_resolve_time_seconds']}s</td></tr>
<tr><td><strong>Unacknowledged:</strong></td><td>{s['unacknowledged_count']}</td></tr>
<tr><td><strong>Escalated:</strong></td><td>{s['escalated_count']}</td></tr>
<tr><td><strong>High Risk Residents:</strong></td><td>{', '.join(s['high_risk_residents']) or 'None'}</td></tr>
<tr><td><strong>Notable Incidents:</strong></td><td>{', '.join(s['notable_incidents']) or 'None'}</td></tr>
</table>
"""

    html = f"""<!DOCTYPE html>
<html>
<head><title>Shift Summary Report</title></head>
<body>
<h1>Shift Summary Report</h1>
<p><strong>Shift ID:</strong> {shift_id}</p>
{summary_sections}
<hr>
<p><em>Generated {dt_to_iso(datetime.now(timezone.utc))} by ElderOS</em></p>
</body>
</html>"""

    return html.encode("utf-8")
