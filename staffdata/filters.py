from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q


def _has_field(model, field_name):
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False


def _apply_common_filters(queryset, params):
    q = (params.get("q") or "").strip()
    supervisor_id = (params.get("supervisor") or "").strip()
    stage = (params.get("stage") or "").strip()
    sector = (params.get("sector") or "").strip()
    school_gender = (params.get("school_gender") or "").strip()
    is_active = (params.get("is_active") or "").strip()

    if q:
        queryset = queryset.filter(
            Q(full_name__icontains=q)
            | Q(national_id__icontains=q)
            | Q(school_name__icontains=q)
            | Q(sector__icontains=q)
        )

    if supervisor_id.isdigit():
        queryset = queryset.filter(supervisor_id=supervisor_id)

    if stage:
        queryset = queryset.filter(stage=stage)

    if sector:
        queryset = queryset.filter(sector=sector)

    if school_gender:
        queryset = queryset.filter(school_gender=school_gender)

    if is_active == "1" and _has_field(queryset.model, "is_active"):
        queryset = queryset.filter(is_active=True)
    elif is_active == "0" and _has_field(queryset.model, "is_active"):
        queryset = queryset.filter(is_active=False)

    if _has_field(queryset.model, "created_at"):
        queryset = queryset.order_by("-created_at")

    return queryset


def apply_principal_filters(request, queryset):
    queryset = _apply_common_filters(queryset, request.GET)

    has_attachment = (request.GET.get("has_attachment") or "").strip()

    if _has_field(queryset.model, "performance_file"):
        if has_attachment == "1":
            queryset = queryset.exclude(performance_file__isnull=True).exclude(performance_file="")
        elif has_attachment == "0":
            queryset = queryset.filter(Q(performance_file__isnull=True) | Q(performance_file=""))

    return queryset


def apply_vice_filters(request, queryset):
    queryset = _apply_common_filters(queryset, request.GET)

    has_attachment = (request.GET.get("has_attachment") or "").strip()

    # إذا كان نموذج الوكيل/الوكيلة لا يملك مرفقًا أصلًا:
    # عند اختيار "يوجد مرفق" نرجع لا شيء
    # وعند اختيار "لا يوجد مرفق" نُبقي النتائج كما هي
    if _has_field(queryset.model, "performance_file"):
        if has_attachment == "1":
            queryset = queryset.exclude(performance_file__isnull=True).exclude(performance_file="")
        elif has_attachment == "0":
            queryset = queryset.filter(Q(performance_file__isnull=True) | Q(performance_file=""))
    else:
        if has_attachment == "1":
            queryset = queryset.none()

    return queryset


def build_filter_choices(principal_qs, vice_qs):
    stage_values = set()
    sector_values = set()
    gender_values = set()
    supervisor_values = {}

    for qs in (principal_qs, vice_qs):
        for value in qs.values_list("stage", flat=True).distinct():
            if value:
                stage_values.add(value)

        for value in qs.values_list("sector", flat=True).distinct():
            if value:
                sector_values.add(value)

        for value in qs.values_list("school_gender", flat=True).distinct():
            if value:
                gender_values.add(value)

        for obj in qs.select_related("supervisor"):
            supervisor = getattr(obj, "supervisor", None)
            if not supervisor:
                continue

            label = None
            for attr in ("full_name", "name", "username"):
                label = getattr(supervisor, attr, None)
                if label:
                    break

            if label:
                supervisor_values[supervisor.id] = str(label)

    return {
        "stages": sorted(stage_values),
        "sectors": sorted(sector_values),
        "school_genders": sorted(gender_values),
        "supervisors": [
            {"id": sid, "label": label}
            for sid, label in sorted(supervisor_values.items(), key=lambda x: x[1])
        ],
    }