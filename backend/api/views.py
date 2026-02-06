from django.http import JsonResponse
from django.shortcuts import render

def health_check(request):
    """
    Endpoint para verificar se a API está online.
    """
    return JsonResponse({
        "status": "online",
        "service": "Ecommerce Analytics API",
        "version": "1.0.0"
    })