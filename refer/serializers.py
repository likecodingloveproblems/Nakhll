from rest_framework import serializers

from nakhll_market.models import Profile


class ReferrerVisitEventSerializer(serializers.Serializer):
    referral_code = serializers.CharField(max_length=6)

    def validate_referral_code(self, value):
        try:
            profile = Profile.objects.select_related(
                'FK_User').get(refer_code=value)
            self.referrer = profile.FK_User
            return value
        except BaseException:
            raise serializers.ValidationError({
                "referral_code": "can't find any user for this referral code."})


class ReferrerEventsReportSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()
