# from django.urls import path
# from . import views

# urlpatterns = [
#     path('login/', views.Login_view, name='login'),
#     path('register/', views.Register_view, name='register'),
#     path('', views.splashscreen, name='splashscreen'),
    
#     #api endpoints
#     path('api-register/', views.RegisterView.as_view(), name='api-register'),
#     path('api-login/', views.LoginView.as_view(), name='api-login'),
    
#     path('create/', views.create_reminder, name='create_reminder'),
#     path('snooze/<int:reminder_id>/<int:minutes>/', views.snooze_reminder, name='snooze_reminder'),
#     path('cancel/<int:reminder_id>/', views.cancel_reminder, name='cancel_reminder'),
#     path('check_reminders/', views.check_reminders, name='check_reminders'),
# ]
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Login_view, name='login'),
    path('register/', views.Register_view, name='register'),
    path('', views.splashscreen, name='splashscreen'),

    # API Endpoints
    path('api-register/', views.RegisterView.as_view(), name='api-register'),
    path('api-login/', views.LoginView.as_view(), name='api-login'),

    # Reminder Endpoints
    path('create-reminder/', views.create_reminder, name='create_reminder'),
    path('start-questionnaire/', views.start_questionnaire, name='start_questionnaire'),  # New URL
    path('voice-create/', views.create_reminder, name='voice_create_reminder'),
    path('snooze/<int:reminder_id>/<int:minutes>/', views.snooze_reminder, name='snooze_reminder'),
    path('cancel/<int:reminder_id>/', views.cancel_reminder, name='cancel_reminder'),
    path('check_reminders/', views.check_reminders, name='check_reminders'),
]
