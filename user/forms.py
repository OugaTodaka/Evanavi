from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserCreationForm(UserCreationForm):
    class Meta:
        def __init__(self, *args, **kwargs ):
            super().__init__(*args, **kwargs)
            self.fields['model'].widget.attrs['class'] = 'box'
        model = User
        fields = ("username", "email")
        labels = {
            "username": "ユーザー名",
            "email": "メールアドレス",
        }
        
class LoginForm(AuthenticationForm):
    class Meta:
        model = User

