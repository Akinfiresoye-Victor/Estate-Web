from django.shortcuts import render, redirect

# Create your views here.
def landing_page(request):
    if not request.user.is_authenticated:
        return render(request, 'core/landing.html')
    else:
        if request.user.role == 'company':
            return redirect('company:dashboard')
        elif request.user.role == 'agent':
            return redirect('agent:dashboard')
        elif request.user.role == 'customer':
            return redirect('customer:user-profile')
        else:
            return render(request, 'core/landing.html')

def about_page(request):
    return render(request, 'core/about.html')