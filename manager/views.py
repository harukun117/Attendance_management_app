from datetime import date, datetime, timedelta
from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from attendance.models import Attendances
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

class ManagerView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'user_list.html'
    login_url = '/accounts/login/'
    def test_func(self):
        user = self.request.user
        return user.is_staff    
 
    def get(self, request, *arg, **kwargs):
        users = User.objects.filter(is_superuser=False)
        context = {
            'users': users
        }
        return self.render_to_response(context)
    
class Manager_user_detailView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'user_detail.html'
    login_url = '/accounts/login/'
    def test_func(self):
        user = self.request.user
        return user.is_staff    
    
    def get(self, request, *org, **kwargs):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        today = datetime.today()
        
        # リクエストパラメータを受け取る
        search_param = request.GET.get('year_month')
        if search_param:
            search_params = list(map(int, search_param.split('-')))
            search_year = search_params[0]
            search_month = search_params[1]
        else:
            search_year = today.year
            search_month = today.month
            
        # 年と月でデータを絞り込む
        month_attendances = Attendances.objects.filter(
            user = user,
            attendance_time__year = search_year,
            attendance_time__month = search_month
        ).order_by('attendance_time')
        
        total_work_hours = timedelta()
        
        for attendance in month_attendances:
            attendance_time = attendance.attendance_time
            leave_time = attendance.leave_time
            
            if leave_time and attendance_time:
                work_duration = leave_time - attendance_time
                total_work_hours += work_duration
                
        total_hours, remainder = divmod(total_work_hours.seconds, 3600)
        total_minutes, _ = divmod(remainder, 60)
        total_work_hours_str = f"{total_hours:02}:{total_minutes:02}"
        
        # context用のデータに整形
        attendances_context = []
        for attendance in month_attendances:
            attendance_time = attendance.attendance_time
            leave_time = attendance.leave_time
            if leave_time:
                leave_time = leave_time.strftime('%H:%M')
            else:
                leave_time = 'not_pushed'
                    
            day_attendance = {
                'id': attendance.id,
                'date': attendance_time.strftime('%Y-%m-%d'),
                'attendance_at': attendance_time.strftime('%H:%M'),
                'leave_at': leave_time
            }
            attendances_context.append(day_attendance)
 
        context = {
            'attendances': attendances_context,
            'user_name': user.username,  
            'user_id': user_id,
            'total_work_time': total_work_hours_str
        }
        # Templateにcontextを含めてレスポンスを返す
        return self.render_to_response(context)
    
class Manager_user_AttendanceEditView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'attendance_edit.html'
    login_url = '/accounts/login/'
    def test_func(self):
        user = self.request.user
        return user.is_staff 
    
    def get(self, request, *org, **kwargs):
        attendance_id = self.kwargs.get('attendance_id')
        attendance = get_object_or_404(Attendances, pk=attendance_id)
        
        leave_time = attendance.leave_time
        if leave_time:
            leave_time = leave_time.strftime('%H:%M')
        else:
            leave_time = 'not_pushed'
        day_attendance = {
                'id': attendance.id,
                'date': attendance.attendance_time.strftime('%Y-%m-%d'),
                'attendance_at': attendance.attendance_time.strftime('%H:%M'),
                'leave_at': leave_time
            }
        user = get_object_or_404(User, pk=attendance.user_id)
        context = {
            'attendance': day_attendance,
            'user_name': user.username
        }
        return self.render_to_response(context)
    
    def post(self, request, *org, **kwargs):
        attendance_id = self.kwargs.get('attendance_id')
        attendance = get_object_or_404(Attendances, pk=attendance_id)
        
        push_date = request.POST.get('push_date')
        push_attendance_time = request.POST.get('push_attendance_time')
        push_leave_time = request.POST.get('push_leave_time')
        
        fix_attendance_datetime = '{}T{}'.format(push_date, push_attendance_time)
        fix_leave_datetime = '{}T{}'.format(push_date, push_leave_time)
        
        attendance.attendance_time = datetime.strptime(fix_attendance_datetime, '%Y-%m-%dT%H:%M')
        attendance.leave_time = datetime.strptime(fix_leave_datetime, '%Y-%m-%dT%H:%M')
        
        attendance.save()
        response_body = {
            'result': 'success'
        }
        return JsonResponse(response_body)
    
class Manager_user_AttendanceRemove(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'user_detail.html'
    login_url = '/accounts/login/'
    def test_func(self):
        user = self.request.user
        return user.is_staff 
    
    def post(self, request, *org, **kwargs):
        attendance_id = request.POST.get('attendanceId')
        attendance = get_object_or_404(Attendances, pk=attendance_id)
        
        attendance.delete()
        response_data = {'message': '削除が成功しました'}
        return JsonResponse(response_data)
