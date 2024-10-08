from django.views.generic import CreateView, TemplateView
from django.http import HttpResponseRedirect
from .forms import UserCreationForm
from django.urls import reverse,reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from .forms import LoginForm
# Create your views here.
class SignUpView(CreateView):

    form_class = UserCreationForm

    template_name = "user/signup.html"

    success_url = reverse_lazy('user:signup_success')

    def form_valid(self, form):
        user = form.save()
        self.object = user
        return super().form_valid(form)

class SignUpSuccessView(TemplateView):
    template_name = "user/signup_success.html"
    
class LoginView(BaseLoginView):
    form_class = LoginForm
    template_name = "user/signin.html"

#    class LogoutView(BaseLogoutView):
#        success_url = reverse_lazy("user:signin")

def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse("user:signin"))