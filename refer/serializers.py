from email.policy import default
from rest_framework import serializers

from nakhll_market.models import Profile
from refer.constants import (
    REFERRER_SIGNUP_REWARD,
    REFERRER_SIGNUP_LIMIT,
    REFERRER_VISIT_REWARD,
    REFERRER_VISIT_LIMIT,
)

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


class ReportField(serializers.DictField):
    status = serializers.IntegerField()
    status_label = serializers.CharField()
    count = serializers.IntegerField(default=0)


class ReferrerEventsReportSerializer(serializers.Serializer):
    report = serializers.ListField(child=ReportField())


class ReferrerVisitEventsReportSerializer(ReferrerEventsReportSerializer):
    limit = serializers.IntegerField(
        default=REFERRER_VISIT_LIMIT,
        initial=REFERRER_VISIT_LIMIT
    )
    reward = serializers.IntegerField(
        default=REFERRER_VISIT_REWARD,
        initial=REFERRER_VISIT_REWARD
    )


class ReferrerSignupEventsReportSerializer(ReferrerEventsReportSerializer):
    limit = serializers.IntegerField(
        default=REFERRER_SIGNUP_LIMIT,
        initial=REFERRER_SIGNUP_LIMIT
    )
    reward = serializers.IntegerField(
        default=REFERRER_SIGNUP_REWARD,
        initial=REFERRER_SIGNUP_REWARD
    )
