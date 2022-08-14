from django.urls import path, include
from rest_framework import routers
from refer.views import ReferrerAnonymousVisitEventViewSet, ReferrerEventsViewSet, ReferrerSignupEventsReportViewSet, ReferrerVisitEventsReportViewSet

app_name = 'refer'

refer_router = routers.DefaultRouter()
refer_router.register(
    'visit',
    ReferrerAnonymousVisitEventViewSet,
    basename='visit')
refer_router.register(
    'visit',
    ReferrerVisitEventsReportViewSet,
    basename='visit')
refer_router.register(
    'signup',
    ReferrerSignupEventsReportViewSet,
    basename='signup')

urlpatterns = [
    path('referrer/', include(refer_router.urls), name='referrer'),
]
