from django.shortcuts import render
from django.db.models import *
from django.db import transaction
from aplicacionesweb_api.serializers import *
from aplicacionesweb_api.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json

class BankAccountsAll(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # Obtener la lista de cuentas bancarias asociadas al usuario actual
        accounts = BankAccount.objects.filter(usuario=request.user)
        account_data = BankAccountSerializer(accounts, many=True).data
        return Response(account_data, 200)

class BankAccountDetailsView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    def get(self, request, *args, **kwargs):
        # Obtener el ID de la cuenta bancaria desde la consulta
        account_id = request.GET.get('id')

        # Verificar si el usuario actual es propietario de la cuenta bancaria
        account = get_object_or_404(BankAccount, id=account_id, user=request.user)

        # Serializar y devolver los detalles de la cuenta bancaria
        serializer = self.get_serializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BankAccountView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        # Verificar si el usuario ya tiene una cuenta bancaria
        existing_account = BankAccount.objects.filter(usuario=request.user).first()

        if existing_account:
            return Response({"message": "Ya tienes una cuenta bancaria"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear una nueva cuenta bancaria para el usuario actual
        serializer = BankAccountSerializer(data={'usuario': request.user.id, 'account_number': generate_account_number()}, context={'request': request})
        
        if serializer.is_valid():
            # Asociar la cuenta bancaria al usuario actual
            serializer.validated_data['usuario'] = request.user
            serializer.save()
            return Response({"message": "Cuenta bancaria creada exitosamente"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class BankAccountViewEdit(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    
    def put(self, request, *args, **kwargs):
        # Obtener la cuenta bancaria y verificar si pertenece al usuario actual
        account_id = request.GET.get('id')
        
        # Verificar si el usuario actual es propietario de la cuenta bancaria
        account = get_object_or_404(BankAccount, id=account_id, user=request.user)
        if account.user == request.user:
            serializer = self.get_serializer(account, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"details": "No tienes permisos para editar esta cuenta bancaria"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        # Obtener el ID de la cuenta bancaria desde la consulta
        account_id = request.GET.get('id')
        # Verificar si el usuario actual es propietario de la cuenta bancaria
        account = get_object_or_404(BankAccount, id=account_id, user=request.user)
        # Eliminar la cuenta bancaria
        account.delete()
        return Response({"details": "Cuenta bancaria eliminada"}, status=status.HTTP_200_OK)

def generate_account_number():
    # Esta función podría generar un número de cuenta único
    # Aquí hay un ejemplo simple de generación, puedes personalizarla según tus necesidades
    return ''.join(random.choices(string.digits, k=10))