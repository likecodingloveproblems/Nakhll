from rest_framework import serializers


class ReferrerAnonymousUniqueVisitSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(max_length=6, null=True)
