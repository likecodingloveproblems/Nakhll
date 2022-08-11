from django.urls import path, include
from rest_framework import routers
from refer.views import ReferrerAnonymousVisitEventViewSet, ReferrerEventsReportViewSet

app_name = 'refer'

visit_router = routers.DefaultRouter()
visit_router.register(
    'visit',
    ReferrerAnonymousVisitEventViewSet,
    basename='visit')
visit_router.register(
    'report',
    ReferrerEventsReportViewSet,
    basename='report')

urlpatterns = [
    path('referrer/', include(visit_router.urls), name='visit'),
]
