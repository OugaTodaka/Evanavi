from django.db import models
from user.models import User

class UserData(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    tel = models.CharField(max_length=15)
    email = models.EmailField()
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    gender = models.CharField(max_length=200)
    birth_date = models.DateField()
    school_name = models.CharField(max_length=200)
    Graduate_Year = models.DateField()
    def __str__(self):
        return self.name

class Eva(models.Model):
    for_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="for_user")
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    detail = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")