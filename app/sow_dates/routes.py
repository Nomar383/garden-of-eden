"""
REST API for sow dates: plant name + date planted.
"""
from datetime import date, datetime

from flask import Blueprint, request, jsonify

from app.models import db, SowDate

sow_dates_blueprint = Blueprint("sow_dates", __name__)


def _parse_date(s: str | None) -> date | None:
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.date()
    except ValueError:
        pass
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


@sow_dates_blueprint.route("", methods=["GET"])
def list_sow_dates():
    """Return all sow date entries, ordered by sow_date desc then id desc."""
    rows = SowDate.query.order_by(SowDate.sow_date.desc(), SowDate.id.desc()).all()
    return jsonify([r.to_dict() for r in rows])


@sow_dates_blueprint.route("", methods=["POST"])
def create_sow_date():
    """Create a sow date entry. Body: plant_name (str), sow_date (ISO date string)."""
    body = request.get_json() or {}
    plant_name = (body.get("plant_name") or "").strip()
    if not plant_name:
        return jsonify({"error": "plant_name is required"}), 400
    sow_d = _parse_date(body.get("sow_date"))
    if sow_d is None:
        return jsonify({"error": "sow_date is required (ISO date, e.g. 2025-02-20)"}), 400
    row = SowDate(plant_name=plant_name, sow_date=sow_d)
    db.session.add(row)
    db.session.commit()
    return jsonify(row.to_dict()), 201


@sow_dates_blueprint.route("/<int:entry_id>", methods=["PATCH", "PUT"])
def update_sow_date(entry_id: int):
    """Update a sow date entry. Body may include plant_name and/or sow_date."""
    row = SowDate.query.get(entry_id)
    if row is None:
        return jsonify({"error": "Not found"}), 404
    body = request.get_json() or {}
    if "plant_name" in body:
        name = (body.get("plant_name") or "").strip()
        if not name:
            return jsonify({"error": "plant_name cannot be empty"}), 400
        row.plant_name = name
    if "sow_date" in body:
        sow_d = _parse_date(body.get("sow_date"))
        if sow_d is None:
            return jsonify({"error": "sow_date must be a valid ISO date"}), 400
        row.sow_date = sow_d
    db.session.commit()
    return jsonify(row.to_dict())


@sow_dates_blueprint.route("/<int:entry_id>", methods=["DELETE"])
def delete_sow_date(entry_id: int):
    """Delete a sow date entry."""
    row = SowDate.query.get(entry_id)
    if row is None:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(row)
    db.session.commit()
    return "", 204
