from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


#@login_required(login_url="login")
def home_view(request):
    if request.user.is_authenticated:
        return render(request, 'home.html', {'user': request.user})
    else:
        return redirect('authSys:login')