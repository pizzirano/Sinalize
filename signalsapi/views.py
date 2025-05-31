from django.shortcuts import render


def home(request):
    return render(request,'signalsapi/pages/home.html', context={
        'name': 'Luis',
    })

