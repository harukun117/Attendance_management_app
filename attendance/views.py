from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Attendances
from datetime import date, datetime, timedelta

class HomeView(LoginRequiredMixin, TemplateView):
    #表示するテンプレート
    template_name = 'home.html'
    
    #ログインがされてなかったらリダイレクトされるURL
    login_url = '/accounts/login/'
    
class PushTimecard(LoginRequiredMixin, TemplateView):
    login_url = '/account/login/'
    #POSTメソッド
    def post(self, request, *args, **kwargs):
        push_type = request.POST.get('push_type')
        
        is_attendanced = Attendances.objects.filter(
            user = request.user,
        ).exists()
        
        response_body = {}
        if push_type == 'attendance':
            #出勤したユーザーをDB保存
            attendance = Attendances(user=request.user)
            attendance.save()
            response_time = attendance.attendance_time
            response_body = {
                'result': 'success',
                'attendance_time': response_time.strftime('%Y-%m-%d %H:%M')
            }
        elif push_type == 'leave':
            if is_attendanced:
                #退勤するユーザーの退勤時間を更新する
                attendance = Attendances.objects.filter(
                    user = request.user,
                    attendance_time__date = date.today()
                ).latest('attendance_time')
                if attendance.leave_time is None:
                    attendance.leave_time = datetime.now()
                    attendance.save()
                    response_time = attendance.leave_time
                    response_body = {
                        'result': 'success',
                        'leave_time': response_time.strftime('%Y-%m-%d %H:%M')
                    }
                else:
                    response_body = {
                        'result': 'not_attended',
                    }
            else:
                response_body = {
                    'result': 'not_attended',
                }
        return JsonResponse(response_body)
    
class AttendanceRecords(LoginRequiredMixin, TemplateView):
    template_name = 'attend_records.html'
    login_url = '/accounts/login'
    def get(self, request, *args, **kwargs):
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
            user = request.user,
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
                'date': attendance_time.strftime('%Y-%m-%d'),
                'attendance_at': attendance_time.strftime('%H:%M'),
                'leave_at': leave_time
            }
            attendances_context.append(day_attendance)
 
        context = {'attendances': attendances_context,
                   'total_work_time': total_work_hours_str
                }
        # Templateにcontextを含めてレスポンスを返す
        return self.render_to_response(context)