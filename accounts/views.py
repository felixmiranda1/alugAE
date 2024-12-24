from django.shortcuts import render

# Create your views here.

def landlord_list(request):
    landlords = ["John Doe", "Jane Smith"]  # Dados fictícios para teste
    return render(request, "landlord_list.html", {"landlords": landlords})
