from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters import rest_framework as filters
from .filters import ReferrerEventFilter

from refer.models import ReferrerSignupEvent, ReferrerVisitEvent
from refer.serializers import (
    ReferrerSignupEventsReportSerializer,
    ReferrerVisitEventSerializer,
    ReferrerVisitEventsReportSerializer,
)


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


class ReferrerEventsViewSet(viewsets.GenericViewSet):
    """abstract referrer events view set"""
    permission_classes = [IsAuthenticated, ]
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ReferrerEventFilter

    def get_queryset(self):
        queryset = self.model.objects.filter(
            referrer=self.request.user)
        return queryset

    def get_report(self):
        queryset = self.filter_queryset(self.get_queryset())
        return {'report': queryset.event_report()}

    @action(detail=False, methods=['get'],
            name='get user referrer visit report')
    def report(self, request):
        report = self.get_report()
        serializer = self.get_serializer(report)
        return Response(serializer.data)


class ReferrerVisitEventsReportViewSet(ReferrerEventsViewSet):
    serializer_class = ReferrerVisitEventsReportSerializer
    model = ReferrerVisitEvent


class ReferrerSignupEventsReportViewSet(ReferrerEventsViewSet):
    serializer_class = ReferrerSignupEventsReportSerializer
    model = ReferrerSignupEvent
