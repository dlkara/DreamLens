from django.db import models
from django.contrib.auth.models import AbstractUser

class DreamDict(models.Model):
    category = models.CharField(max_length=50)   # 대분류
    keyword = models.CharField(max_length=50)    # 소분류 키워드
    meaning = models.TextField()                 # 상징적 의미

    def __str__(self):
        return f"[{self.category}] {self.keyword}"


# ----------------------------------------------------------------
# Users 모델
# ----------------------------------------------------------------
class User(AbstractUser):
    # 기본 필드(username, password, email 등)는 AbstractUser에 이미 포함
    # password는 Django가 자동으로 안전하게 해싱하여 저장

    # related_name을 추가하여 기본 User 모델과의 충돌을 방지
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='dreamlens_user_groups',  # 충돌 방지를 위한 별명
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='dreamlens_user_permissions',  # 충돌 방지를 위한 별명
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    nickname = models.CharField(
        max_length=50,
        unique=False,
    )
    birth = models.DateField(
        null=True,  # 선택적 정보이므로 비어있을 수 있음
        blank=True,  # 관리자 페이지에서도 비워둘 수 있도록 허용
    )
    gender = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )
    # 소셜 로그인을 위한 필드
    provider = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    provider_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'🟨 Users [id={self.id}, username={self.username}, created_at={self.created_at}]'


# ----------------------------------------------------------------
# Interpretation 모델
# ----------------------------------------------------------------
class Interpretation(models.Model):
    """
    AI가 생성한 해몽 결과와 관련 로그를 저장
    """
    user = models.ForeignKey(
        User,  # User 모델과의 관계를 설정
        on_delete=models.CASCADE,  # User가 삭제되면, 관련된 해몽 기록도 함께 삭제
    )
    input_text = models.TextField(blank=True)
    result = models.TextField()
    keywords = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    summary = models.TextField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        # 데이터베이스에 표시될 순서를 최신순으로 정렬
        ordering = ['-created_at']

    def __str__(self):
        return f"🟦 {self.user.username}님의 해몽 요청 (ID: {self.id})"


from django.utils import timezone

class Emotion(models.Model):
    """
    꿈을 꿀 때 느낀 감정(기쁨, 슬픔, 두려움 등)을 저장하는 모델
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="감정")

    class Meta:
        verbose_name = "감정"
        verbose_name_plural = "감정 목록"

    def __str__(self):
        return self.name


class DreamType(models.Model):
    """
    꿈의 유형(예: 비행, 추락, 추격 등)을 저장하는 모델
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="꿈 유형")

    class Meta:
        verbose_name = "꿈 유형"
        verbose_name_plural = "꿈 유형 목록"

    def __str__(self):
        return self.name


class Diary(models.Model):
    """
    사용자가 기록한 꿈 일기
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="diaries",
        verbose_name="작성자"
    )
    interpretation = models.ForeignKey(
        Interpretation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diary_entries",
        verbose_name="해몽"
    )
    emotion = models.ForeignKey(
        Emotion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diaries",
        verbose_name="감정"
    )
    dream_type = models.ForeignKey(
        DreamType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diaries",
        verbose_name="꿈 유형"
    )
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name="꿈꾼 날짜"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="등록 시각"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정 시각"
    )

    class Meta:
        verbose_name = "꿈 일기"
        verbose_name_plural = "꿈 일기 목록"
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username}님의 꿈 일기 ({self.date:%Y-%m-%d %H:%M})"
