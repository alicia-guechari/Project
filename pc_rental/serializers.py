from rest_framework import serializers
from .models import *

class PCSerializer(serializers.ModelSerializer):
    class Meta:
        model = PC
        fields = '__all__'

class RentalSerializer(serializers.ModelSerializer):
    pc = serializers.ReadOnlyField(source='pc.name')
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {
            'username' : obj.user.username,
            'email' : obj.user.email,
            'phone' : obj.user.phone,
        }

    class Meta:
        model = Rental
        fields = '__all__'
        read_only_fields = ['user']