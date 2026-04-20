from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class Supervisor(models.Model):
    full_name = models.CharField("اسم المشرف", max_length=255)
    national_id = models.CharField("السجل المدني", max_length=10, unique=True)
    password = models.CharField("كلمة المرور", max_length=255, blank=True, default="")
    mobile = models.CharField("رقم الجوال", max_length=20, blank=True)
    email = models.EmailField("البريد الإلكتروني", blank=True)
    is_active = models.BooleanField("نشط", default=True)

    # صلاحيات المشرف على السجلات
    can_add_records = models.BooleanField("يستطيع إضافة السجلات", default=True)
    can_edit_records = models.BooleanField("يستطيع تعديل السجلات", default=False)
    can_delete_records = models.BooleanField("يستطيع حذف السجلات", default=False)

    # تفعيل الحساب
    is_activated = models.BooleanField("تم تفعيل الحساب", default=False)
    password_set_at = models.DateTimeField("تاريخ إنشاء/تحديث كلمة المرور", null=True, blank=True)
    last_login_at = models.DateTimeField("آخر دخول", null=True, blank=True)

    created_at = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "مشرف"
        verbose_name_plural = "المشرفون"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} - {self.national_id}"

    def save(self, *args, **kwargs):
        if self.national_id:
            self.national_id = "".join(filter(str.isdigit, self.national_id))

        if self.password and not self.password.startswith(
            ("pbkdf2_sha256$", "argon2$", "bcrypt$", "scrypt$")
        ):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.password_set_at = timezone.now()

    def check_password(self, raw_password):
        if not self.password:
            return False
        return check_password(raw_password, self.password)