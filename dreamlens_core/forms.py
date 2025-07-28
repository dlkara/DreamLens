from django import forms

class DreamForm(forms.Form):
    dream = forms.CharField(
        label="꿈 내용을 입력하세요",
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": "예: 나는 강아지를 업고 있었어"})
    )
