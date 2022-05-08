# from django.contrib.admin import AdminSite
#
#
# class ReportsAdminSite(AdminSite):
#     site_header = "Panel for get reports"
#     site_title = "Nakhll reports panel"
#     index_title = "Welcome to Nakhll reports panel"
#
#     def has_permission(self, request):
#         """
#         Return True if the given HttpRequest has permission to view
#         *at least one* page in the admin site.
#         """
#         groups = request.user.groups.all()
#         if request.user.is_active and request.user.is_staff:
#             # if request.user.is_active and request.user.is_staff and 'reports' in [group.name for group in groups]:
#             return True
#         return False
#
#
# reports_admin_site = ReportsAdminSite(name='reports_admin')
