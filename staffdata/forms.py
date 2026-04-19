from django import forms

from accounts.models import Supervisor

from .models import CorrectionRequest, PrincipalRecord, VicePrincipalRecord


class StyledModelForm(forms.ModelForm):
    text_input_types = (
        forms.TextInput,
        forms.NumberInput,
        forms.EmailInput,
        forms.PasswordInput,
        forms.URLInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            css_class = "form-control"

            if isinstance(field.widget, forms.Select):
                css_class = "form-select"
            elif isinstance(field.widget, forms.Textarea):
                css_class = "form-control"
                field.widget.attrs.setdefault("rows", 3)
            elif isinstance(field.widget, forms.ClearableFileInput):
                css_class = "form-control"
            elif isinstance(field.widget, forms.CheckboxInput):
                css_class = "form-check-input"

            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_class} {css_class}".strip()

            if isinstance(field.widget, self.text_input_types):
                field.widget.attrs.setdefault("autocomplete", "off")


def normalize_mobile_value(value):
    digits = "".join(filter(str.isdigit, str(value or "").strip()))

    if digits.startswith("966") and len(digits) == 12:
        digits = "0" + digits[3:]
    elif digits.startswith("5") and len(digits) == 9:
        digits = "0" + digits

    return digits


class BaseStaffRecordForm(StyledModelForm):
    def __init__(self, *args, **kwargs):
        self.lock_supervisor = kwargs.pop("lock_supervisor", False)
        self.show_supervisor = kwargs.pop("show_supervisor", False)
        super().__init__(*args, **kwargs)

        self._setup_common_ui()
        self._setup_supervisor_field()
        self._setup_meta_flags()
        self._setup_field_order()

    def _setup_common_ui(self):
        if "full_name" in self.fields:
            self.fields["full_name"].widget.attrs.setdefault("placeholder", "الاسم الرباعي")

        if "national_id" in self.fields:
            self.fields["national_id"].widget.attrs.update({
                "maxlength": "10",
                "inputmode": "numeric",
                "placeholder": "10 أرقام",
            })

        if "mobile" in self.fields:
            self.fields["mobile"].widget.attrs.update({
                "maxlength": "14",
                "inputmode": "numeric",
                "placeholder": "05XXXXXXXX",
            })

        if "role" in self.fields:
            self.fields["role"].widget.attrs.setdefault("data-field", "role")

        if "stage" in self.fields:
            self.fields["stage"].widget.attrs.setdefault("data-field", "stage")

        if "sector" in self.fields:
            self.fields["sector"].widget.attrs.setdefault("placeholder", "اسم القطاع")

        if "school_name" in self.fields:
            self.fields["school_name"].widget.attrs.setdefault("placeholder", "اسم المدرسة")

        if "school_gender" in self.fields:
            self.fields["school_gender"].widget.attrs.setdefault("data-field", "school_gender")

        if "notes" in self.fields:
            self.fields["notes"].widget.attrs.setdefault("placeholder", "ملاحظات إضافية إن وجدت")

    def _setup_supervisor_field(self):
        if "supervisor" not in self.fields:
            return

        if self.show_supervisor:
            self.fields["supervisor"].required = True
            if self.lock_supervisor and self.instance and self.instance.pk:
                self.fields["supervisor"].disabled = True
        else:
            self.fields.pop("supervisor")

    def _setup_meta_flags(self):
        if "is_active" in self.fields:
            self.fields["is_active"].required = False

    def _setup_field_order(self):
        preferred_order = [
            "full_name",
            "national_id",
            "mobile",
            "role",
            "stage",
            "sector",
            "school_name",
            "school_gender",
            "performance_file",
            "notes",
            "is_active",
        ]

        if self.show_supervisor and "supervisor" in self.fields:
            preferred_order = ["supervisor", *preferred_order]

        self.order_fields([name for name in preferred_order if name in self.fields])

    def clean_national_id(self):
        value = self.cleaned_data.get("national_id", "")
        return "".join(filter(str.isdigit, value or ""))

    def clean_mobile(self):
        return normalize_mobile_value(self.cleaned_data.get("mobile", ""))


class PrincipalRecordForm(BaseStaffRecordForm):
    class Meta:
        model = PrincipalRecord
        fields = [
            "supervisor",
            "full_name",
            "national_id",
            "mobile",
            "role",
            "stage",
            "sector",
            "school_name",
            "school_gender",
            "performance_file",
            "notes",
            "is_active",
        ]


class VicePrincipalRecordForm(BaseStaffRecordForm):
    class Meta:
        model = VicePrincipalRecord
        fields = [
            "supervisor",
            "full_name",
            "national_id",
            "mobile",
            "role",
            "stage",
            "sector",
            "school_name",
            "school_gender",
            "notes",
            "is_active",
        ]


class CorrectionRequestForm(StyledModelForm):
    ACTION_ROLE_CHOICES = (
        PrincipalRecord.ROLE_CHOICES + VicePrincipalRecord.ROLE_CHOICES
    )

    requested_role = forms.ChoiceField(
        label="الصفة المقترحة",
        choices=ACTION_ROLE_CHOICES,
    )

    class Meta:
        model = CorrectionRequest
        fields = [
            "reason",
            "requested_full_name",
            "requested_national_id",
            "requested_mobile",
            "requested_role",
            "requested_stage",
            "requested_sector",
            "requested_school_name",
            "requested_school_gender",
            "requested_notes",
            "requested_performance_file",
        ]
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 4}),
            "requested_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.target_type = kwargs.pop("target_type", None)
        super().__init__(*args, **kwargs)

        if "reason" in self.fields:
            self.fields["reason"].help_text = "اذكر الخطأ القائم وسبب طلب التصحيح بشكل واضح."

        if "requested_full_name" in self.fields:
            self.fields["requested_full_name"].widget.attrs.setdefault("placeholder", "الاسم الرباعي")

        if "requested_national_id" in self.fields:
            self.fields["requested_national_id"].widget.attrs.update({
                "maxlength": "10",
                "inputmode": "numeric",
                "placeholder": "10 أرقام",
            })

        if "requested_mobile" in self.fields:
            self.fields["requested_mobile"].widget.attrs.update({
                "maxlength": "14",
                "inputmode": "numeric",
                "placeholder": "05XXXXXXXX",
            })

        if "requested_sector" in self.fields:
            self.fields["requested_sector"].widget.attrs.setdefault("placeholder", "اسم القطاع")

        if "requested_school_name" in self.fields:
            self.fields["requested_school_name"].widget.attrs.setdefault("placeholder", "اسم المدرسة")

        if "requested_notes" in self.fields:
            self.fields["requested_notes"].widget.attrs.setdefault("placeholder", "ملاحظات إضافية إن وجدت")

        self.fields["requested_performance_file"].required = False

        if self.target_type == CorrectionRequest.TARGET_PRINCIPAL:
            self.fields["requested_role"].choices = PrincipalRecord.ROLE_CHOICES

        elif self.target_type == CorrectionRequest.TARGET_VICE:
            self.fields["requested_role"].choices = VicePrincipalRecord.ROLE_CHOICES
            self.fields["requested_performance_file"].widget = forms.HiddenInput()
            self.fields["requested_performance_file"].required = False

    def clean_requested_national_id(self):
        value = self.cleaned_data.get("requested_national_id", "")
        return "".join(filter(str.isdigit, value or ""))

    def clean_requested_mobile(self):
        return normalize_mobile_value(self.cleaned_data.get("requested_mobile", ""))


class CorrectionDecisionForm(forms.Form):
    ACTION_APPROVE = "approve"
    ACTION_RETURN = "return"
    ACTION_REJECT = "reject"

    ACTION_CHOICES = [
        (ACTION_APPROVE, "اعتماد التصحيح"),
        (ACTION_RETURN, "إعادة للمشرف"),
        (ACTION_REJECT, "رفض الطلب"),
    ]

    action = forms.ChoiceField(
        label="الإجراء",
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    admin_note = forms.CharField(
        label="ملاحظة الإدارة",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
            }
        ),
    )


class SupervisorImportForm(forms.Form):
    file = forms.FileField(
        label="ملف المشرفين",
        help_text="يرفع ملف Excel بصيغة .xlsx ويحتوي على الأعمدة: full_name, national_id, mobile, email, is_active",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": ".xlsx",
            }
        ),
    )

    update_existing = forms.BooleanField(
        label="تحديث المشرفين الموجودين مسبقًا",
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    reset_existing_accounts = forms.BooleanField(
        label="إعادة تهيئة الحسابات الموجودة أثناء التحديث",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        help_text="عند تفعيل هذا الخيار سيتم إلغاء كلمة المرور الحالية وإرجاع الحساب إلى حالة الدخول الأول.",
    )

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not file:
            return file

        name = (file.name or "").lower()
        if not name.endswith(".xlsx"):
            raise forms.ValidationError("يرجى رفع ملف Excel بصيغة .xlsx فقط.")

        return file


class SupervisorAdminUpdateForm(StyledModelForm):
    class Meta:
        model = Supervisor
        fields = [
            "full_name",
            "national_id",
            "mobile",
            "email",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "full_name" in self.fields:
            self.fields["full_name"].widget.attrs.setdefault("placeholder", "الاسم الكامل للمشرف")
            self.fields["full_name"].help_text = "يكتب الاسم كما هو معتمد إداريًا."

        if "national_id" in self.fields:
            self.fields["national_id"].widget.attrs.update({
                "maxlength": "10",
                "inputmode": "numeric",
                "placeholder": "10 أرقام",
                "readonly": "readonly",
            })
            self.fields["national_id"].disabled = True
            self.fields["national_id"].help_text = "السجل المدني معروض للمراجعة فقط ولا يحرر من هذه الصفحة."

        if "mobile" in self.fields:
            self.fields["mobile"].widget.attrs.update({
                "maxlength": "14",
                "inputmode": "numeric",
                "placeholder": "05XXXXXXXX",
            })
            self.fields["mobile"].help_text = "سيستخدم هذا الرقم في الدخول الأول إذا كان الحساب غير مفعّل."

        if "email" in self.fields:
            self.fields["email"].required = False
            self.fields["email"].widget.attrs.setdefault("placeholder", "example@email.com")

        if "is_active" in self.fields:
            self.fields["is_active"].required = False

        self.order_fields([
            name for name in [
                "full_name",
                "national_id",
                "mobile",
                "email",
                "is_active",
            ]
            if name in self.fields
        ])

    def clean_national_id(self):
        if self.instance and self.instance.pk:
            return self.instance.national_id
        value = self.cleaned_data.get("national_id", "")
        return "".join(filter(str.isdigit, value or ""))

    def clean_mobile(self):
        digits = normalize_mobile_value(self.cleaned_data.get("mobile", ""))

        if not digits:
            raise forms.ValidationError("رقم الجوال مطلوب.")

        if not (digits.startswith("05") and len(digits) == 10):
            raise forms.ValidationError("رقم الجوال يجب أن يكون بصيغة صحيحة مثل 05XXXXXXXX.")

        return digits

    def clean_email(self):
        return (self.cleaned_data.get("email") or "").strip()

    def clean_full_name(self):
        value = (self.cleaned_data.get("full_name") or "").strip()
        if not value:
            raise forms.ValidationError("اسم المشرف مطلوب.")
        return value