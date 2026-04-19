from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # تسجيل الدخول والخروج
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # إنشاء كلمة المرور بعد الدخول الأول
    path("activate/set-password/", views.activate_account_set_password_view, name="activate_account_set_password"),

    # استعادة كلمة المرور (صفحة توجيهية فقط)
    path("forgot-password/", views.forgot_password_start_view, name="forgot_password_start"),

    # الملف الشخصي
    path("profile/", views.profile_view, name="profile"),
    path("profile/password/", views.change_password_view, name="change_password"),
]