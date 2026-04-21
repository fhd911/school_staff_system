from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.utils import timezone

from accounts.models import Supervisor


def _normalize_digits(value):
    return "".join(filter(str.isdigit, (value or "").strip()))


def _normalize_mobile(value):
    digits = _normalize_digits(value)

    if digits.startswith("966") and len(digits) == 12:
        digits = "0" + digits[3:]
    elif digits.startswith("5") and len(digits) == 9:
        digits = "0" + digits

    return digits


class ManualSchoolStaffBase(models.Model):
    STAGE_CHOICES = [
        ("ابتدائي", "ابتدائي"),
        ("متوسط", "متوسط"),
        ("ثانوي", "ثانوي"),
        ("رياض أطفال", "رياض أطفال"),
        ("مجمع", "مجمع"),
        ("أخرى", "أخرى"),
    ]

    SCHOOL_GENDER_CHOICES = [
        ("بنين", "بنين"),
        ("بنات", "بنات"),
    ]

    MOBILE_VALIDATOR = RegexValidator(
        regex=r"^(05\d{8}|9665\d{8})$",
        message="يجب أن يكون رقم الجوال بصيغة 05XXXXXXXX أو 9665XXXXXXXX.",
    )

    supervisor = models.ForeignKey(
        Supervisor,
        on_delete=models.CASCADE,
        verbose_name="المشرف",
    )
    full_name = models.CharField("الاسم الرباعي", max_length=255)
    national_id = models.CharField(
        "السجل المدني",
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$",
                message="يجب أن يكون السجل المدني 10 أرقام.",
            )
        ],
    )
    mobile = models.CharField(
        "رقم الجوال",
        max_length=20,
        blank=True,
        validators=[MOBILE_VALIDATOR],
    )
    school_name = models.CharField("اسم المدرسة", max_length=255)
    sector = models.CharField("القطاع", max_length=100)
    stage = models.CharField("المرحلة الدراسية", max_length=50, choices=STAGE_CHOICES)
    school_gender = models.CharField("نوع المدرسة", max_length=10, choices=SCHOOL_GENDER_CHOICES)
    notes = models.TextField("ملاحظات", blank=True)
    is_active = models.BooleanField("نشط", default=True)
    created_at = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.national_id = _normalize_digits(self.national_id)
        self.mobile = _normalize_mobile(self.mobile)
        self.full_name = (self.full_name or "").strip()
        self.school_name = (self.school_name or "").strip()
        self.sector = (self.sector or "").strip()
        super().save(*args, **kwargs)

    def _display_value(self, value):
        if value is None:
            return ""
        if hasattr(value, "name") and getattr(value, "name", None):
            return str(value.name).strip()
        return str(value).strip()

    def _supervisor_attr(self, *attr_names):
        if not self.supervisor_id or not self.supervisor:
            return ""
        for attr_name in attr_names:
            value = getattr(self.supervisor, attr_name, "")
            if value:
                return self._display_value(value)
        return ""

    @property
    def supervisor_name_display(self):
        return (
            self._supervisor_attr("full_name", "name", "display_name")
            or self._display_value(self.supervisor)
        )

    @property
    def supervisor_national_id_display(self):
        return self._supervisor_attr(
            "national_id",
            "civil_id",
            "identity_number",
            "id_number",
        )

    @property
    def supervisor_mobile_display(self):
        return self._supervisor_attr(
            "mobile",
            "phone",
            "phone_number",
            "mobile_number",
        )

    @property
    def supervisor_sector_display(self):
        if self.sector:
            return self.sector.strip()

        return self._supervisor_attr(
            "sector",
            "sector_name",
        )


class PrincipalRecord(ManualSchoolStaffBase):
    ROLE_CHOICES = [
        ("مدير", "مدير"),
        ("مديرة", "مديرة"),
    ]

    ASSIGNMENT_STATUS_CHOICES = [
        ("رسمي", "رسمي"),
        ("مسير", "مسير"),
    ]

    role = models.CharField("الصفة", max_length=10, choices=ROLE_CHOICES)
    assignment_status = models.CharField(
        "الحالة الإدارية",
        max_length=10,
        choices=ASSIGNMENT_STATUS_CHOICES,
        default="رسمي",
    )
    performance_file = models.FileField(
        "استمارة الأداء الوظيفي",
        upload_to="performance_forms/%Y/%m/",
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
    )

    class Meta:
        verbose_name = "سجل مدير/مديرة"
        verbose_name_plural = "سجلات المديرين/المديرات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.school_name}"

    def clean(self):
        existing = PrincipalRecord.objects.filter(
            school_name=(self.school_name or "").strip(),
            sector=(self.sector or "").strip(),
            stage=self.stage,
            school_gender=self.school_gender,
            is_active=True,
        ).exclude(pk=self.pk)

        if existing.exists():
            raise ValidationError("يوجد مدير/مديرة فعال لهذه المدرسة بالفعل.")


class VicePrincipalRecord(ManualSchoolStaffBase):
    ROLE_CHOICES = [
        ("وكيل", "وكيل"),
        ("وكيلة", "وكيلة"),
    ]

    role = models.CharField("الصفة", max_length=10, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = "سجل وكيل/وكيلة"
        verbose_name_plural = "سجلات الوكلاء/الوكيلات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.school_name}"

    def clean(self):
        existing = VicePrincipalRecord.objects.filter(
            national_id=_normalize_digits(self.national_id),
            school_name=(self.school_name or "").strip(),
            role=self.role,
            is_active=True,
        ).exclude(pk=self.pk)

        if existing.exists():
            raise ValidationError("هذا الوكيل/الوكيلة مسجل مسبقًا لهذه المدرسة.")


class CorrectionRequest(models.Model):
    TARGET_PRINCIPAL = "principal"
    TARGET_VICE = "vice"
    TARGET_TYPE_CHOICES = [
        (TARGET_PRINCIPAL, "مدير/مديرة"),
        (TARGET_VICE, "وكيل/وكيلة"),
    ]

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_RETURNED = "returned"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "قيد المراجعة"),
        (STATUS_APPROVED, "تم الاعتماد"),
        (STATUS_RETURNED, "أعيد للمشرف"),
        (STATUS_REJECTED, "مرفوض"),
    ]

    MOBILE_VALIDATOR = RegexValidator(
        regex=r"^(05\d{8}|9665\d{8})$",
        message="يجب أن يكون رقم الجوال بصيغة 05XXXXXXXX أو 9665XXXXXXXX.",
    )

    supervisor = models.ForeignKey(
        Supervisor,
        on_delete=models.CASCADE,
        related_name="correction_requests",
        verbose_name="المشرف",
    )

    target_type = models.CharField(
        "نوع السجل",
        max_length=20,
        choices=TARGET_TYPE_CHOICES,
    )

    principal_record = models.ForeignKey(
        PrincipalRecord,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="correction_requests",
        verbose_name="سجل المدير/المديرة",
    )

    vice_record = models.ForeignKey(
        VicePrincipalRecord,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="correction_requests",
        verbose_name="سجل الوكيل/الوكيلة",
    )

    reason = models.TextField("سبب طلب التصحيح")

    requested_full_name = models.CharField("الاسم الرباعي المقترح", max_length=255)
    requested_national_id = models.CharField(
        "السجل المدني المقترح",
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$",
                message="يجب أن يكون السجل المدني 10 أرقام.",
            )
        ],
    )
    requested_mobile = models.CharField(
        "رقم الجوال المقترح",
        max_length=20,
        blank=True,
        validators=[MOBILE_VALIDATOR],
    )
    requested_school_name = models.CharField("اسم المدرسة المقترح", max_length=255)
    requested_sector = models.CharField("القطاع المقترح", max_length=100)
    requested_stage = models.CharField(
        "المرحلة الدراسية المقترحة",
        max_length=50,
        choices=ManualSchoolStaffBase.STAGE_CHOICES,
    )
    requested_school_gender = models.CharField(
        "نوع المدرسة المقترح",
        max_length=10,
        choices=ManualSchoolStaffBase.SCHOOL_GENDER_CHOICES,
    )
    requested_role = models.CharField("الصفة المقترحة", max_length=10)
    requested_notes = models.TextField("الملاحظات المقترحة", blank=True)

    requested_performance_file = models.FileField(
        "المرفق المقترح",
        upload_to="correction_requests/%Y/%m/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
    )

    status = models.CharField(
        "الحالة",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    admin_note = models.TextField("ملاحظة الإدارة", blank=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staffdata_reviewed_corrections",
        verbose_name="مراجع الطلب",
    )
    reviewed_at = models.DateTimeField("تاريخ المراجعة", null=True, blank=True)

    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "طلب تصحيح"
        verbose_name_plural = "طلبات التصحيح"
        ordering = ["-created_at"]

    def __str__(self):
        return f"طلب تصحيح - {self.get_target_type_display()} - {self.supervisor}"

    @property
    def target_record(self):
        if self.target_type == self.TARGET_PRINCIPAL:
            return self.principal_record
        return self.vice_record

    def save(self, *args, **kwargs):
        self.requested_national_id = _normalize_digits(self.requested_national_id)
        self.requested_mobile = _normalize_mobile(self.requested_mobile)
        self.requested_full_name = (self.requested_full_name or "").strip()
        self.requested_school_name = (self.requested_school_name or "").strip()
        self.requested_sector = (self.requested_sector or "").strip()
        super().save(*args, **kwargs)

    def clean(self):
        errors = {}

        if self.target_type == self.TARGET_PRINCIPAL:
            if not self.principal_record:
                errors["principal_record"] = "يجب تحديد سجل المدير/المديرة."
            if self.vice_record:
                errors["vice_record"] = "لا يمكن ربط طلب مدير/مديرة بسجل وكيل/وكيلة."
        elif self.target_type == self.TARGET_VICE:
            if not self.vice_record:
                errors["vice_record"] = "يجب تحديد سجل الوكيل/الوكيلة."
            if self.principal_record:
                errors["principal_record"] = "لا يمكن ربط طلب وكيل/وكيلة بسجل مدير/مديرة."

        target = self.target_record
        if target and self.supervisor_id and target.supervisor_id != self.supervisor_id:
            errors["supervisor"] = "السجل المطلوب تصحيحه لا يتبع هذا المشرف."

        if self.target_type == self.TARGET_VICE and self.requested_performance_file:
            errors["requested_performance_file"] = "سجل الوكيل/الوكيلة لا يدعم رفع مرفق تصحيح."

        if errors:
            raise ValidationError(errors)


class AccountResetRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSED = "processed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "قيد المعالجة"),
        (STATUS_PROCESSED, "تمت المعالجة"),
        (STATUS_CANCELLED, "ملغي"),
    ]

    supervisor = models.ForeignKey(
        Supervisor,
        on_delete=models.CASCADE,
        related_name="account_reset_requests",
        verbose_name="المشرف",
    )

    status = models.CharField(
        "الحالة",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    notes = models.TextField("ملاحظات", blank=True)

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staffdata_processed_account_reset_requests",
        verbose_name="تمت المعالجة بواسطة",
    )
    processed_at = models.DateTimeField("تاريخ المعالجة", null=True, blank=True)

    created_at = models.DateTimeField("تاريخ الطلب", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "طلب إعادة تهيئة حساب"
        verbose_name_plural = "طلبات إعادة تهيئة الحسابات"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["supervisor"],
                condition=models.Q(status="pending"),
                name="unique_pending_account_reset_request_per_supervisor",
            )
        ]

    def __str__(self):
        return f"طلب إعادة تهيئة - {self.supervisor.full_name}"

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @property
    def is_processed(self):
        return self.status == self.STATUS_PROCESSED

    def clean(self):
        if self.status == self.STATUS_PROCESSED:
            if not self.processed_at:
                raise ValidationError({"processed_at": "يجب تحديد تاريخ المعالجة عند اعتماد الطلب."})
            if not self.processed_by:
                raise ValidationError({"processed_by": "يجب تحديد المستخدم الذي عالج الطلب."})


class DataEntryWindow(models.Model):
    title = models.CharField("اسم الفترة", max_length=200, default="فترة تسجيل البيانات")
    starts_at = models.DateTimeField("بداية الفترة")
    ends_at = models.DateTimeField("نهاية الفترة")
    is_active = models.BooleanField("مفعلة", default=True)
    allow_add = models.BooleanField("السماح بالإضافة", default=True)
    allow_edit = models.BooleanField("السماح بالتعديل", default=False)
    allow_delete = models.BooleanField("السماح بالحذف", default=False)
    notes = models.TextField("ملاحظات", blank=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "فترة تسجيل البيانات"
        verbose_name_plural = "فترات تسجيل البيانات"
        ordering = ["-starts_at"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "يجب أن يكون وقت نهاية الفترة بعد وقت البداية."})

    @property
    def is_open_now(self):
        now = timezone.now()
        return self.is_active and self.starts_at <= now <= self.ends_at

    @property
    def has_started(self):
        return timezone.now() >= self.starts_at

    @property
    def has_ended(self):
        return timezone.now() > self.ends_at

    @property
    def remaining_seconds(self):
        if not self.is_open_now:
            return 0
        remaining = int((self.ends_at - timezone.now()).total_seconds())
        return max(remaining, 0)

    @property
    def remaining_days(self):
        return self.remaining_seconds // 86400

    @property
    def remaining_hours(self):
        return self.remaining_seconds // 3600

    @property
    def status_label(self):
        now = timezone.now()
        if not self.is_active:
            return "غير مفعلة"
        if now < self.starts_at:
            return "لم تبدأ"
        if self.starts_at <= now <= self.ends_at:
            return "مفتوحة"
        return "منتهية"
