from django.db.models import Count
from rest_framework import views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from .serializer import ReferrerAnonymousUniqueVisitSerializer

from refer.models import ReferrerEventStatuses, ReferrerVisitEvent
from nakhll_market.models import Profile

from refer import serializer


class ReferrerAnonymousUniqueVisit(views.APIView):
    permission_classes = [AllowAny, ]
    serializer_class = ReferrerAnonymousUniqueVisitSerializer

    def post(self, request):
        serializer = ReferrerAnonymousUniqueVisitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        referral_code = serializer.validated_data['referral_code']
        try:
            profile = Profile.objects.select_related(
                'FK_User').get(refer_code=referral_code)
        except Profile.DoesNotExist:
            '''when referrer does not exists, it's not possible to find two profile for one
            refer_code, because it's unique.'''
            return Response('', status=HTTP_400_BAD_REQUEST)
        ReferrerVisitEvent.objects.create(
            referrer=profile.FK_User, request=request)
        return Response('', status=HTTP_201_CREATED)

    @action(detail=False, methods=['GET'],
            url_path='report', permission_classes=[IsAuthenticated, ])
    def report(self, request):
        '''return a report to user about it's referral visitors'''
        report = ReferrerVisitEvent.objects.filter(
            referrer=request.user).aggregate(
            new=Count(
                'pk', status=ReferrerEventStatuses.NEW), processed=Count(
                'pk', status=ReferrerEventStatuses.PROCESSED), inactive=Count(
                'pk', status=ReferrerEventStatuses.INACTIVE), )
        return Response(report)
