from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.status import HTTP_201_CREATED

from refer.models import ReferrerSignupEvent, ReferrerVisitEvent
from refer.serializers import ReferrerEventsReportSerializer, ReferrerVisitEventSerializer


class ReferrerAnonymousVisitEventViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = ReferrerVisitEventSerializer

    @action(methods=['post'], detail=False)
    def set(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ReferrerVisitEvent.objects.create(
            referrer=serializer.referrer, request=request)
        return Response(serializer.data)


class ReferrerEventsReportViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ReferrerEventsReportSerializer

    def get_object(self):
        return

    @action(detail=False, methods=['get'])
    def signup(self, request):
        data = ReferrerSignupEvent.objects.event_report(referrer=request.user)
        return Response(data)

    @action(detail=False, methods=['get'])
    def visit(self, request):
        '''return a report to user about it's referral visitors'''
        return Response(
            ReferrerVisitEvent.objects.event_report(referrer=request.user))
