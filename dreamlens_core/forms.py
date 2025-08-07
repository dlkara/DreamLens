from django import forms
from django.contrib.auth import get_user_model
from .models import Diary, DreamType, Emotion
from django.utils import timezone

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


# ------------------------------------------
# dreamtype, emotion select 만들기
# ------------------------------------------
class DiaryForm(forms.ModelForm):
    """
    Diary 모델을 기반으로 한 폼.
    ForeignKey로 연결된 DreamType과 Emotion은 자동으로 Select 박스로 렌더링
    """
    # DB에서 선택지를 가져와 '선택하기' 옵션을 추가합니다.
    dream_type = forms.ModelChoiceField(
        queryset=DreamType.objects.all(),
        empty_label="선택하세요",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="꿈 종류"
    )
    emotion = forms.ModelChoiceField(
        queryset=Emotion.objects.all(),
        empty_label="선택하세요",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="꿈 감정"
    )

    class Meta:
        model = Diary
        # 폼에서 사용자에게 직접 입력받을 필드들을 지정합니다.
        fields = ['date', 'dream_type', 'emotion']

        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                # 오늘 날짜를 기본값으로 설정
                format='%Y-%m-%d'
            ),
        }
        labels = {
            'date': '날짜 선택',
        }

    def __init__(self, *args, **kwargs):
        super(DiaryForm, self).__init__(*args, **kwargs)
        # 폼이 처음 로드될 때 오늘 날짜를 기본값으로 설정
        if 'initial' not in kwargs:
            self.fields['date'].initial =timezone.localdate()

