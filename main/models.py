from django.db import models
from user.models import User
from django.core.validators import MinLengthValidator

class UserData(models.Model):
    GENDER_CHOICES = [
        (0, '男性'),
        (1, '女性'),
        (2, 'その他'),
    ]
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    tel = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    zip_code = models.CharField(max_length=255)
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0)
    birth_date = models.DateField()
    school_name = models.CharField(max_length=200)
    graduate_Year = models.DateField()
    group_code = models.CharField(max_length=20, validators=[MinLengthValidator(3)])
    
    def __str__(self):
        return self.name

class Eva(models.Model):
    for_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="for_user")
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    detail = models.CharField(max_length=200)
    pub_date = models.DateTimeField(auto_now_add=True)
    
class Status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Userモデルへの外部キー

    # 1〜5までの範囲でステータスを保存
    sociability = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])  # 社交性
    knowledge = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])    # 知識
    qualification = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 6)])  # 資格
    sociability_point = models.IntegerField(default=0)  # 社交性を上げるためのポイント
    knowledge_point = models.IntegerField(default=0)    # 知識を上げるためのポイント
    qualification_point = models.IntegerField(default=0)    # 資格を上げるためのポイント

    class Meta:
        verbose_name_plural = 'ステータス'

    def __str__(self):
        return f"{self.user.username}のステータス"