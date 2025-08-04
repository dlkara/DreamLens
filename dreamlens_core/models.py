from django.db import models

class DreamDict(models.Model):
    category = models.CharField(max_length=50)   # 대분류
    keyword = models.CharField(max_length=50)    # 소분류 키워드
    meaning = models.TextField()                 # 상징적 의미

    def __str__(self):
        return f"[{self.category}] {self.keyword}"
