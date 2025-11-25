from django.shortcuts import render

def index_view(request):
    """
    Página de inicio (Landing Page)
    """
    # Si el usuario ya está autenticado, redirigirlo al dashboard
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('dashboard:home')
    
    return render(request, 'index.html')