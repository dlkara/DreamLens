from django import forms
from django.contrib.auth import get_user_model

class DreamForm(forms.Form):
    dream = forms.CharField(
        label="꿈 내용을 입력하세요",
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": "예: 나는 강아지를 업고 있었어"})
    )

User = get_user_model()

class MyPageForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label="새 비밀번호"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label="새 비밀번호 확인"
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'nickname', 'birth', 'gender']
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
            self.instance.set_password(password)

        return cleaned_data
