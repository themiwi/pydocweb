from pydocweb.docweb.utils import *
import re

from views_wiki import frontpage
from models import set_user_default_groups

#------------------------------------------------------------------------------
# User management
#------------------------------------------------------------------------------

class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class PasswordChangeForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True,
                               min_length=7)
    password_verify = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_verify'):
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data

class RegistrationForm(forms.Form):
    username = forms.CharField(required=True, min_length=4)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True,
                               min_length=7)
    password_verify = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        user = self.cleaned_data.get('username')
        if not user or not re.match('^[a-z0-9_]+$', user):
            raise forms.ValidationError("User name can contain only alphanumeric "
                                        "characters and underscores")
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_verify'):
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data

def login(request):
    message = ""
    if request.method == 'POST':
        time.sleep(2) # thwart password cracking
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'],
                                password=data['password'])
            if user is not None and user.is_active:
                auth_login(request, user)
                target = request.POST.get('next')
                if target is None: target = reverse(frontpage)
                return HttpResponseRedirect(target)
            else:
                message = "Authentication failed"

    # Never send the password etc. back
    form = LoginForm()

    return render_template(request, 'registration/login.html',
                           dict(form=form, message=message))

@login_required
def password_change(request):
    message = ""
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            request.user.set_password(data['password'])
            request.user.first_name = data['first_name']
            request.user.last_name = data['last_name']
            request.user.email = data['email']
            request.user.save()
            message = "Profile and password updated."
    else:
        form = PasswordChangeForm(
            initial=dict(first_name=request.user.first_name,
                         last_name=request.user.last_name,
                         email=request.user.email,
                         password="",
                         password_verify=""))

    return render_template(request, 'registration/change_password.html',
                           dict(form=form, message=message))

def register(request):
    message = ""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            count = User.objects.filter(username=data['username']).count()
            if count == 0 and data['username'].lower() not in ('xml-import', 'source'):
                user = User.objects.create_user(data['username'],
                                                data['email'],
                                                data['password'])
                user.first_name = data['first_name']
                user.last_name = data['last_name']
                set_user_default_groups(user)
                user.save()
                return render_template(request,
                                       'registration/register_done.html',
                                       dict(username=data['username']))
            else:
                message = "User name %s is already reserved" % data['username']
    else:
        form = RegistrationForm()

    return render_template(request, 'registration/register.html',
                           dict(form=form, message=message))
