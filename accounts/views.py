from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from staffdata.models import AccountResetRequest

from .decorators import get_current_supervisor, supervisor_login_required
from .forms import SupervisorLoginForm
from .models import Supervisor


ARABIC_TO_ENGLISH_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

ACTIVATION_SESSION_SUPERVISOR_ID = "activation_supervisor_id"
ACTIVATION_SESSION_VERIFIED = "activation_verified"
ACTIVATION_SESSION_STARTED_AT = "activation_started_at"
ACTIVATION_TIMEOUT_MINUTES = 30


# =========================
# Helpers
# =========================
def _normalize_digits(value):
    value = (value or "").strip().translate(ARABIC_TO_ENGLISH_DIGITS)
    return "".join(filter(str.isdigit, value))


def _normalize_national_id(value):
    return _normalize_digits(value)


def _normalize_mobile(value):
    digits = _normalize_digits(value)

    if digits.startswith("966") and len(digits) == 12:
        digits = "0" + digits[3:]
    elif digits.startswith("5") and len(digits) == 9:
        digits = "0" + digits

    return digits


def _get_supervisor_by_national_id(national_id):
    return Supervisor.objects.filter(
        national_id=national_id,
    ).first()


def _supervisor_is_activated(supervisor):
    return bool(getattr(supervisor, "is_activated", False))


def _touch_last_login(supervisor):
    if hasattr(supervisor, "last_login_at"):
        supervisor.last_login_at = timezone.now()
        supervisor.save(update_fields=["last_login_at"])


def _mark_supervisor_login(request, supervisor):
    request.session["supervisor_id"] = supervisor.id
    request.session["supervisor_name"] = supervisor.full_name
    _touch_last_login(supervisor)


def _begin_activation_session(request, supervisor):
    request.session[ACTIVATION_SESSION_SUPERVISOR_ID] = supervisor.id
    request.session[ACTIVATION_SESSION_VERIFIED] = True
    request.session[ACTIVATION_SESSION_STARTED_AT] = timezone.now().timestamp()
    request.session.modified = True


def _clear_activation_session(request):
    request.session.pop(ACTIVATION_SESSION_SUPERVISOR_ID, None)
    request.session.pop(ACTIVATION_SESSION_VERIFIED, None)
    request.session.pop(ACTIVATION_SESSION_STARTED_AT, None)
    request.session.modified = True


def _get_activation_supervisor(request):
    supervisor_id = request.session.get(ACTIVATION_SESSION_SUPERVISOR_ID)
    if not supervisor_id:
        return None
    return Supervisor.objects.filter(pk=supervisor_id, is_active=True).first()


def _activation_session_expired(request):
    started_at = request.session.get(ACTIVATION_SESSION_STARTED_AT)
    if not started_at:
        return True

    expires_at = float(started_at) + (ACTIVATION_TIMEOUT_MINUTES * 60)
    return timezone.now().timestamp() > expires_at


def _can_use_mobile_for_first_login(supervisor, entered_password):
    if not supervisor or _supervisor_is_activated(supervisor):
        return False

    saved_mobile = _normalize_mobile(getattr(supervisor, "mobile", ""))
    entered_mobile = _normalize_mobile(entered_password)

    if not saved_mobile or not entered_mobile:
        return False

    return saved_mobile == entered_mobile


def _validate_new_password(supervisor, password1, password2):
    if not password1 or not password2:
        return "يرجى تعبئة حقول كلمة المرور."

    if password1 != password2:
        return "كلمتا المرور غير متطابقتين."

    if len(password1) < 8:
        return "يجب ألا تقل كلمة المرور عن 8 أحرف."

    if _normalize_digits(password1) == _normalize_national_id(getattr(supervisor, "national_id", "")):
        return "لا يمكن أن تكون كلمة المرور مطابقة للسجل المدني."

    if _normalize_digits(password1) == _normalize_mobile(getattr(supervisor, "mobile", "")):
        return "لا يمكن أن تكون كلمة المرور الجديدة مطابقة لرقم الجوال."

    return ""


def _get_open_account_reset_request(supervisor):
    return (
        AccountResetRequest.objects.filter(
            supervisor=supervisor,
            status=AccountResetRequest.STATUS_PENDING,
        )
        .order_by("-created_at")
        .first()
    )


def _create_account_reset_request(supervisor):
    open_request = _get_open_account_reset_request(supervisor)
    if open_request:
        return open_request, False

    try:
        with transaction.atomic():
            reset_request = AccountResetRequest.objects.create(
                supervisor=supervisor,
                status=AccountResetRequest.STATUS_PENDING,
            )
        return reset_request, True
    except IntegrityError:
        open_request = _get_open_account_reset_request(supervisor)
        return open_request, False


# =========================
# Login
# =========================
def login_view(request):
    if request.session.get("supervisor_id"):
        return redirect("staffdata:dashboard")

    form = SupervisorLoginForm(request.POST or None)
    error_message = ""

    if request.method == "POST" and form.is_valid():
        national_id = _normalize_national_id(form.cleaned_data["national_id"])
        password = form.cleaned_data["password"]

        supervisor = _get_supervisor_by_national_id(national_id)

        if not supervisor:
            error_message = "بيانات الدخول غير صحيحة."

        elif not getattr(supervisor, "is_active", True):
            error_message = "هذا الحساب غير نشط. يرجى مراجعة الإدارة."

        elif not _supervisor_is_activated(supervisor):
            if not _normalize_mobile(supervisor.mobile):
                error_message = "لا يوجد رقم جوال مسجل لهذا الحساب. يرجى مراجعة الإدارة."
            elif _can_use_mobile_for_first_login(supervisor, password):
                _begin_activation_session(request, supervisor)
                messages.info(
                    request,
                    "تم التحقق من الدخول الأول. يرجى الآن إنشاء كلمة مرور جديدة.",
                )
                return redirect("accounts:activate_account_set_password")
            else:
                error_message = "في أول دخول تكون كلمة المرور هي رقم الجوال المسجل في النظام."

        elif supervisor.check_password(password):
            _mark_supervisor_login(request, supervisor)
            return redirect("staffdata:dashboard")

        else:
            error_message = "بيانات الدخول غير صحيحة."

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "error_message": error_message,
        },
    )


# =========================
# Legacy activation routes
# =========================
def activate_account_start_view(request):
    return redirect("accounts:login")


def activate_account_verify_view(request):
    return redirect("accounts:login")


def activate_account_set_password_view(request):
    supervisor = _get_activation_supervisor(request)
    is_verified = request.session.get(ACTIVATION_SESSION_VERIFIED, False)

    if not supervisor or not is_verified:
        messages.warning(
            request,
            "لم يتم التحقق من الدخول الأول. استخدم رقم الجوال في أول دخول من صفحة الدخول الرئيسية.",
        )
        return redirect("accounts:login")

    if _activation_session_expired(request):
        _clear_activation_session(request)
        messages.error(request, "انتهت جلسة الدخول الأول. يرجى إعادة المحاولة من صفحة الدخول.")
        return redirect("accounts:login")

    if _supervisor_is_activated(supervisor):
        _clear_activation_session(request)
        messages.info(request, "تم تفعيل هذا الحساب مسبقًا. يمكنك تسجيل الدخول مباشرة.")
        return redirect("accounts:login")

    if request.method == "POST":
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        validation_error = _validate_new_password(supervisor, password1, password2)
        if validation_error:
            messages.error(request, validation_error)
        else:
            supervisor.set_password(password1)
            supervisor.is_activated = True

            update_fields = ["password", "is_activated"]
            if hasattr(supervisor, "password_set_at"):
                update_fields.append("password_set_at")

            supervisor.save(update_fields=update_fields)
            _clear_activation_session(request)

            messages.success(request, "تم إنشاء كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول.")
            return redirect("accounts:login")

    return render(
        request,
        "accounts/activate_account_set_password.html",
        {
            "page_title": "إنشاء كلمة المرور",
            "supervisor": supervisor,
        },
    )


# =========================
# Forgot password
# =========================
def forgot_password_start_view(request):
    if request.session.get("supervisor_id"):
        return redirect("staffdata:dashboard")

    if request.method == "POST":
        national_id = _normalize_national_id(request.POST.get("national_id"))

        if not national_id:
            messages.error(request, "يرجى إدخال السجل المدني.")
            return redirect("accounts:forgot_password_start")

        supervisor = _get_supervisor_by_national_id(national_id)

        if not supervisor:
            messages.error(request, "لا توجد بيانات مشرف مطابقة لهذا السجل المدني.")
            return redirect("accounts:forgot_password_start")

        if not getattr(supervisor, "is_active", True):
            messages.error(request, "هذا الحساب غير نشط حاليًا. يرجى مراجعة الإدارة.")
            return redirect("accounts:forgot_password_start")

        if not _supervisor_is_activated(supervisor):
            messages.info(
                request,
                "هذا الحساب لم يُفعّل بعد. يمكنك الدخول أول مرة باستخدام رقم الجوال المسجل في النظام.",
            )
            return redirect("accounts:login")

        reset_request, created = _create_account_reset_request(supervisor)

        if created:
            messages.success(
                request,
                "تم إرسال طلب إعادة تهيئة الحساب إلى الإدارة بنجاح. سيتم إشعارك أو خدمتك بعد المعالجة وفق الإجراء المعتمد.",
            )
        else:
            messages.info(
                request,
                "يوجد بالفعل طلب إعادة تهيئة مفتوح لهذا الحساب وهو قيد المعالجة لدى الإدارة.",
            )

        return redirect("accounts:forgot_password_start")

    return render(
        request,
        "accounts/forgot_password_start.html",
        {
            "page_title": "استعادة كلمة المرور",
        },
    )


def forgot_password_verify_view(request):
    return redirect("accounts:forgot_password_start")


def forgot_password_reset_view(request):
    return redirect("accounts:forgot_password_start")


# =========================
# Profile
# =========================
@supervisor_login_required
def profile_view(request):
    supervisor = get_current_supervisor(request)

    return render(
        request,
        "accounts/profile.html",
        {
            "page_title": "ملفي الشخصي",
            "supervisor": supervisor,
        },
    )


@supervisor_login_required
def change_password_view(request):
    supervisor = get_current_supervisor(request)

    if request.method == "POST":
        current_password = request.POST.get("current_password", "")
        new_password1 = request.POST.get("new_password1", "")
        new_password2 = request.POST.get("new_password2", "")

        if not current_password or not new_password1 or not new_password2:
            messages.error(request, "يرجى تعبئة جميع الحقول.")
        elif not supervisor.check_password(current_password):
            messages.error(request, "كلمة المرور الحالية غير صحيحة.")
        else:
            validation_error = _validate_new_password(supervisor, new_password1, new_password2)
            if validation_error:
                messages.error(request, validation_error)
            else:
                supervisor.set_password(new_password1)

                update_fields = ["password"]
                if hasattr(supervisor, "password_set_at"):
                    update_fields.append("password_set_at")

                supervisor.save(update_fields=update_fields)

                messages.success(request, "تم تغيير كلمة المرور بنجاح.")
                return redirect("accounts:profile")

    return render(
        request,
        "accounts/change_password.html",
        {
            "page_title": "تغيير كلمة المرور",
            "supervisor": supervisor,
        },
    )


# =========================
# Logout
# =========================
def logout_view(request):
    request.session.flush()
    return redirect("accounts:login")