from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from bank.models import Account


class AccountReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            'net_balance',
            'net_cashable_amount',
            'requests_coin_report',
        )

    def create(self, validated_data):
        return ValidationError('Cannot create an account')

    def update(self, instance, validated_data):
        return ValidationError('Cannot update an account')

    def save(self, **kwargs):
        return ValidationError('Cannot save an account')
