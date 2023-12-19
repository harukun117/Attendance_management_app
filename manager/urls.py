from django.urls import path
from .views import ManagerView ,Manager_user_detailView, Manager_user_AttendanceEditView, Manager_user_AttendanceRemove


urlpatterns = [
    path('manager', ManagerView.as_view(), name='manager'),
    path('manager/<int:user_id>/', Manager_user_detailView.as_view(), name='manager_user_detail'),
    path('manager/<int:attendance_id>/edit/', Manager_user_AttendanceEditView.as_view(), name='manager_user_attendanceEdit'),
    path('remove', Manager_user_AttendanceRemove.as_view(), name='remove')
]