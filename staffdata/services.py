from collections import defaultdict
from django.core.exceptions import FieldDoesNotExist


def _has_field(model, field_name):
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


def _safe_attr(obj, *names, default="—"):
    for name in names:
        value = getattr(obj, name, None)
        if value not in (None, ""):
            return value
    return default


def _display_value(value, default="—"):
    if value in (None, ""):
        return default
    if hasattr(value, "name") and getattr(value, "name", None):
        return str(value.name).strip()
    return str(value).strip()


def _supervisor_attr(supervisor, *names, default="—"):
    if supervisor is None:
        return default

    for name in names:
        value = getattr(supervisor, name, None)
        if value not in (None, ""):
            return _display_value(value, default=default)

    return default


def _supervisor_label(supervisor):
    if supervisor is None:
        return "غير محدد"

    for attr in ("full_name", "name", "username"):
        value = getattr(supervisor, attr, None)
        if value:
            return str(value)

    return str(supervisor)


def _supervisor_national_id(supervisor):
    return _supervisor_attr(
        supervisor,
        "national_id",
        "civil_id",
        "identity_number",
        "id_number",
        default="—",
    )


def _supervisor_mobile(supervisor):
    return _supervisor_attr(
        supervisor,
        "mobile",
        "phone",
        "phone_number",
        "mobile_number",
        default="—",
    )


def _supervisor_sector(supervisor):
    return _supervisor_attr(
        supervisor,
        "sector",
        "sector_name",
        default="—",
    )


def _supports_attachment(obj):
    return _has_field(obj.__class__, "performance_file")


def _has_attachment(obj):
    if not _supports_attachment(obj):
        return False

    value = getattr(obj, "performance_file", None)
    if not value:
        return False

    try:
        return bool(value.name)
    except Exception:
        return False


def _attachment_url(obj):
    if not _supports_attachment(obj):
        return ""

    file_obj = getattr(obj, "performance_file", None)
    if not file_obj:
        return ""

    try:
        return file_obj.url
    except Exception:
        return ""


def _is_active(obj):
    if not _has_field(obj.__class__, "is_active"):
        return False
    return bool(getattr(obj, "is_active", False))


def _record_dict(obj, role_label):
    supervisor = getattr(obj, "supervisor", None)
    supports_attachment = _supports_attachment(obj)
    has_attachment = _has_attachment(obj)

    supervisor_id = getattr(obj, "supervisor_id", None)
    if not supervisor_id and supervisor is not None:
        supervisor_id = getattr(supervisor, "id", None)

    return {
        "id": getattr(obj, "id", 0),
        "role_label": role_label,
        "full_name": _safe_attr(obj, "full_name"),
        "national_id": _safe_attr(obj, "national_id"),
        "school_name": _safe_attr(obj, "school_name"),
        "sector": _safe_attr(obj, "sector"),
        "stage": _safe_attr(obj, "stage"),
        "school_gender": _safe_attr(obj, "school_gender"),
        "supervisor_id": supervisor_id,
        "supervisor_name": _supervisor_label(supervisor),
        "supervisor_sector": _supervisor_sector(supervisor),
        "supervisor_national_id": _supervisor_national_id(supervisor),
        "supervisor_mobile": _supervisor_mobile(supervisor),
        "is_active": _is_active(obj),
        "supports_attachment": supports_attachment,
        "has_attachment": has_attachment,
        "file_url": _attachment_url(obj),
    }


def build_admin_overview_context(principal_qs, vice_qs):
    principal_items = [_record_dict(obj, "مدير / مديرة") for obj in principal_qs]
    vice_items = [_record_dict(obj, "وكيل / وكيلة") for obj in vice_qs]

    all_items = principal_items + vice_items

    principal_total = len(principal_items)
    vice_total = len(vice_items)
    total_records = len(all_items)

    active_records = sum(1 for item in all_items if item["is_active"])
    inactive_records = total_records - active_records

    attachable_records = [item for item in all_items if item["supports_attachment"]]
    attached_records = sum(1 for item in attachable_records if item["has_attachment"])
    missing_attachments = sum(1 for item in attachable_records if not item["has_attachment"])

    school_names = {
        item["school_name"]
        for item in all_items
        if item["school_name"] not in ("", "—")
    }
    schools_total = len(school_names)

    supervisor_map = defaultdict(
        lambda: {
            "supervisor_id": None,
            "supervisor_name": "",
            "sector": "—",
            "national_id": "—",
            "mobile": "—",
            "principals": 0,
            "vices": 0,
            "total": 0,
            "active": 0,
            "missing_attachments": 0,
        }
    )

    def _supervisor_key(item):
        if item["supervisor_id"]:
            return f"id:{item['supervisor_id']}"
        return f"name:{item['supervisor_name']}"

    for item in principal_items:
        key = _supervisor_key(item)

        supervisor_map[key]["supervisor_id"] = item["supervisor_id"]
        supervisor_map[key]["supervisor_name"] = item["supervisor_name"]

        if supervisor_map[key]["sector"] == "—":
            supervisor_map[key]["sector"] = (
                item["supervisor_sector"]
                if item["supervisor_sector"] not in ("", "—")
                else item["sector"]
            )

        if supervisor_map[key]["national_id"] == "—":
            supervisor_map[key]["national_id"] = item["supervisor_national_id"]

        if supervisor_map[key]["mobile"] == "—":
            supervisor_map[key]["mobile"] = item["supervisor_mobile"]

        supervisor_map[key]["principals"] += 1
        supervisor_map[key]["total"] += 1

        if item["is_active"]:
            supervisor_map[key]["active"] += 1

        if item["supports_attachment"] and not item["has_attachment"]:
            supervisor_map[key]["missing_attachments"] += 1

    for item in vice_items:
        key = _supervisor_key(item)

        supervisor_map[key]["supervisor_id"] = item["supervisor_id"]
        supervisor_map[key]["supervisor_name"] = item["supervisor_name"]

        if supervisor_map[key]["sector"] == "—":
            supervisor_map[key]["sector"] = (
                item["supervisor_sector"]
                if item["supervisor_sector"] not in ("", "—")
                else item["sector"]
            )

        if supervisor_map[key]["national_id"] == "—":
            supervisor_map[key]["national_id"] = item["supervisor_national_id"]

        if supervisor_map[key]["mobile"] == "—":
            supervisor_map[key]["mobile"] = item["supervisor_mobile"]

        supervisor_map[key]["vices"] += 1
        supervisor_map[key]["total"] += 1

        if item["is_active"]:
            supervisor_map[key]["active"] += 1

        if item["supports_attachment"] and not item["has_attachment"]:
            supervisor_map[key]["missing_attachments"] += 1

    supervisor_rows = sorted(
        supervisor_map.values(),
        key=lambda x: (
            -x["missing_attachments"],
            -x["total"],
            x["supervisor_name"] or "",
        ),
    )

    sector_map = defaultdict(int)
    stage_map = defaultdict(int)

    for item in all_items:
        sector_label = item["sector"] if item["sector"] not in ("", "—") else "غير محدد"
        stage_label = item["stage"] if item["stage"] not in ("", "—") else "غير محدد"
        sector_map[sector_label] += 1
        stage_map[stage_label] += 1

    sector_rows = [
        {"label": label, "count": count}
        for label, count in sorted(sector_map.items(), key=lambda x: (-x[1], x[0]))
    ]

    stage_rows = [
        {"label": label, "count": count}
        for label, count in sorted(stage_map.items(), key=lambda x: (-x[1], x[0]))
    ]

    recent_records = sorted(all_items, key=lambda x: x["id"], reverse=True)[:12]

    return {
        "principal_total": principal_total,
        "vice_total": vice_total,
        "total_records": total_records,
        "active_records": active_records,
        "inactive_records": inactive_records,
        "attachments_total": attached_records,
        "missing_attachments": missing_attachments,
        "schools_total": schools_total,
        "stats": {
            "total_records": total_records,
            "total_principals": principal_total,
            "total_vices": vice_total,
            "active_records": active_records,
            "inactive_records": inactive_records,
            "attached_records": attached_records,
            "missing_attachments": missing_attachments,
            "schools_total": schools_total,
            "supervisors_count": len(supervisor_rows),
        },
        "supervisor_rows": supervisor_rows,
        "sector_rows": sector_rows,
        "stage_rows": stage_rows,
        "recent_records": recent_records,
    }