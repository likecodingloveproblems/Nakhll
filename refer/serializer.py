from rest_framework import serializers


class ReferrerAnonymousUniqueVisitSerializer(serializers.Serializer):
    referral_code = serializers.CharField(max_length=6)
