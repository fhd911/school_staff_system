from django import forms


class SupervisorLoginForm(forms.Form):
    national_id = forms.CharField(
        label="السجل المدني",
        max_length=10,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "أدخل السجل المدني",
            "dir": "ltr",
        }),
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "أدخل كلمة المرور",
        }),
    )

    def clean_national_id(self):
        value = self.cleaned_data["national_id"]
        value = "".join(filter(str.isdigit, value))
        if len(value) != 10:
            raise forms.ValidationError("يجب أن يكون السجل المدني 10 أرقام.")
        return value