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