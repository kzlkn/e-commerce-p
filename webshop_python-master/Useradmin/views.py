from django.contrib.auth import login as authorize_login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic
from .forms import MySignUpForm
from .models import ExtendedUser, get_extended_user_from_user
from django.contrib.auth.decorators import login_required


class MyLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        authorize_login(self.request, form.get_user())
        user = form.get_user()
        extended_user = get_extended_user_from_user(user)
        if extended_user is not None:  # users are only saved after they logged in after creating account
            extended_user.execute_after_login()

        return HttpResponseRedirect(self.get_success_url())


class MySignUpView(generic.CreateView):
    form_class = MySignUpForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def form_valid(self, form):
        data = form.cleaned_data
        user = User.objects.create_user(username=data['username'],
                                        password=data['password'],
                                        first_name=data['first_name'],
                                        last_name=data['last_name'],
                                        email=data['email'],
                                        )

        extended_user = ExtendedUser.objects.create(user=user,
                                                    date_of_birth=data['date_of_birth'],
                                                    profile_picture=data['profile_picture'],
                                                    gender=data['gender'],
                                                    street=data['street'],
                                                    house_number=data['house_number'],
                                                    plz=data['plz'],
                                                    city=data['city'],
                                                    mobile_number=data['mobile_number']
                                                    )

        return redirect('/')


@login_required(login_url='/useradmin/login')
def user_profile(request):
    extended_user = get_extended_user_from_user(request.user)
    full_name = extended_user.get_full_name_of_user()
    address = extended_user.get_address_of_user()
    context = {
        'extended_user': extended_user,
        'address': address,
        'full_name': full_name
    }
    return render(request, 'user-profile.html', context)


def edit_user_profile(request, user_id: str):
    # extended_user = ExtendedUser.objects.get(id=int(user_id))
    # extended_user_form = MySignUpForm(request.POST or None, instance=extended_user)
    # context = {'user_form': user_form, 'extended_user_form': extended_user_form}

    user = User.objects.get(id=int(user_id))
    user_form = MySignUpForm(request.POST or None, instance=user)
    context = {'user_form': user_form}
    contentOfPage = render(request, 'user-profile-edit.html', context)

    # if user_form.is_valid() and extended_user_form.is_valid():
    if user_form.is_valid():
        user_form.save()
        # extended_user_form.save()
        return redirect('user-profile')
    return contentOfPage
