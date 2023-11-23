from rest_framework import serializers
from rest_framework.authtoken.models import Token
from aplicacionesweb_api.models import *

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email')

class ProfilesSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Profiles
        fields = "__all__"
class ProfilesAllSerializer(serializers.ModelSerializer):
    #user=UserSerializer(read_only=True)
    class Meta:
        model = Profiles
        fields = '__all__'
        depth = 1

class BankAccountSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )
    usuario = UserSerializer(read_only=True)
    class Meta:
        model = BankAccount
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    # usuario = serializers.PrimaryKeyRelatedField(
    #     default=serializers.CurrentUserDefault(),
    #     read_only=True,
    # )
    
    class Meta:
        model = Transaction
        fields = '__all__'


