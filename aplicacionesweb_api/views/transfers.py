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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from aplicacionesweb_api.serializers import TransactionSerializer
from aplicacionesweb_api.models import BankAccount
from aplicacionesweb_api.models import Transaction
import string
import random
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_money(request):
    # Obtener datos de la transferencia desde la solicitud
    sender_account_number = request.data.get('sender_account_number')
    receiver_account_number = request.data.get('receiver_account_number')
    amount = request.data.get('amount')

    # Verificar si las cuentas existen y pertenecen al usuario actual
    sender_account = get_object_or_404(BankAccount, account_number=sender_account_number, usuario=request.user)
    receiver_account = get_object_or_404(BankAccount, account_number=receiver_account_number, usuario=request.user)

    # Verificar si el saldo en la cuenta del remitente es suficiente
    if sender_account.balance < amount:
        return Response({"details": "Saldo insuficiente para realizar la transferencia"}, status=status.HTTP_400_BAD_REQUEST)

    # Realizar la transferencia
    with transaction.atomic():
        # Actualizar el saldo del remitente y receptor
        sender_account.balance -= amount
        receiver_account.balance += amount
        sender_account.save()
        receiver_account.save()

        # Registrar la transacción
        transaction_data = {
            'sender_account': sender_account.id,
            'receiver_account': receiver_account.id,
            'amount': amount,
        }
        transaction_serializer = TransactionSerializer(data=transaction_data)
        if transaction_serializer.is_valid():
            transaction_serializer.save()
        else:
            return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Transferencia realizada exitosamente"}, status=status.HTTP_201_CREATED)
