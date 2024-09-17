from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")
        labels = {
            "username": "ユーザー名",
            "email": "メールアドレス",
        }
        
class LoginForm(AuthenticationForm):
    class Meta:
        model = User

