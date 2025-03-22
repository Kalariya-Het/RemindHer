from django.contrib.auth import authenticate, login
from .utils.voice_assistant import run_questionnaire  # Relative import from app
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import User, Reminder, VoiceResponse
from .serializers import UserSerializer
from rest_framework.parsers import JSONParser, FormParser
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from celery import shared_task
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json
from django.http import HttpResponse, JsonResponse
import dateparser
from .utils.voice_assistant import run_questionnaire  # Import from utils
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .utils.voice_assistant import run_questionnaire
import traceback
# Existing views unchanged
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not registered'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        if user.status != 'Active':
            return Response({'error': 'Account is inactive'}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)

def Login_view(request):
    return render(request, 'Login.html')

def Register_view(request):
    return render(request, 'Register.html')

def splashscreen(request):
    return render(request, 'splashscreen.html')

@login_required
def create_reminder(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task = data.get('task')
            time_str = data.get('time')
            date_str = data.get('date')
            reminder_type = data.get('type')

            # Parse time and date from spoken input
            try:
                task_time = dateparser.parse(time_str, settings={'TIMEZONE': 'UTC', 'RETURN_AS_TIMEZONE_AWARE': False}).time() if time_str else None
                task_date = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'}).date() if date_str else None
            except Exception as e:
                return JsonResponse({'error': f"Invalid time or date format: {str(e)}"}, status=400)

            # Validate all required fields
            if not all([task, task_time, task_date, reminder_type]):
                return JsonResponse({'error': 'Missing or invalid input'}, status=400)

            # Create the reminder
            reminder = Reminder.objects.create(
                user=request.user,
                task=task,
                task_time=task_time,
                task_date=task_date,
                reminder_type=reminder_type
            )

            # Schedule the reminder
            schedule_reminder(reminder)
            return JsonResponse({
                'message': 'Reminder set successfully',
                'reminder_id': reminder.id
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"An error occurred: {str(e)}"}, status=500)

    # Render the template for GET requests
    return render(request, 'create_reminder.html')

@shared_task
def play_ringtone(reminder_id):
    from playsound import playsound
    reminder = Reminder.objects.get(id=reminder_id)
    playsound('static/images/marco.mp3')  # Ensure this path is correct
    reminder.is_completed = True
    reminder.save()

def schedule_reminder(reminder):
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=reminder.task_time.minute,
        hour=reminder.task_time.hour,
        day_of_month=reminder.task_date.day,
        month_of_year=reminder.task_date.month,
    )
    PeriodicTask.objects.create(
        crontab=schedule,
        name=f'reminder-{reminder.id}',
        task='RemindHer_app.views.play_ringtone',
        args=json.dumps([reminder.id]),
        one_off=reminder.reminder_type.lower() == 'once'
    )

@login_required
def snooze_reminder(request, reminder_id, minutes):
    try:
        reminder = Reminder.objects.get(id=reminder_id, user=request.user)
        new_time = (datetime.combine(reminder.task_date, reminder.task_time) + timedelta(minutes=minutes)).time()
        reminder.task_time = new_time
        reminder.is_completed = False
        reminder.save()
        schedule_reminder(reminder)
        return JsonResponse({'message': 'Reminder snoozed'})
    except Reminder.DoesNotExist:
        return JsonResponse({'error': 'Reminder not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def cancel_reminder(request, reminder_id):
    try:
        reminder = Reminder.objects.get(id=reminder_id, user=request.user)
        reminder.is_completed = True
        reminder.save()
        PeriodicTask.objects.filter(name=f'reminder-{reminder.id}').delete()
        return JsonResponse({'message': 'Reminder canceled'})
    except Reminder.DoesNotExist:
        return JsonResponse({'error': 'Reminder not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def check_reminders(request):
    now = datetime.now()
    reminders = Reminder.objects.filter(
        user=request.user,
        task_date=now.date(),
        task_time__hour=now.hour,
        task_time__minute=now.minute,
        is_completed=False
    )
    if reminders.exists():
        reminder = reminders.first()
        return JsonResponse({
            'reminder': {'id': reminder.id, 'task': reminder.task}
        })
    return JsonResponse({'reminder': None})

# New view for voice questionnaire@login_required
@login_required
@csrf_exempt
def start_questionnaire(request):
    print("START: Entering start_questionnaire view")
    print(f"Request Method: {request.method}")
    print(f"Request Headers: {dict(request.headers)}")
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    print(f"Is AJAX request? {is_ajax}")
    
    if is_ajax and request.method == 'POST':
        user_id = request.user.id
        print(f"User ID: {user_id}")
        
        try:
            data = json.loads(request.body)
            responses = data.get('responses', {})
            print(f"Received responses: {responses}")
            
            if not responses:
                return JsonResponse({'message': 'No responses provided'}, status=400)
            
            for question, response in responses.items():
                # Truncate to fit max_length=255
                question = question[:255] if len(question) > 255 else question
                response = response[:255] if len(response) > 255 else response
                VoiceResponse.objects.create(user=request.user, question=question, response=response)
            
            confirmation = f"Here’s what {request.user.email} said: "
            for q, r in responses.items():
                confirmation += f"{q} - {r}. "
            
            return JsonResponse({
                'message': 'Questionnaire completed and saved',
                'confirmation': confirmation
            }, status=200)
        except Exception as e:
            print(f"Error in start_questionnaire: {e}")
            return JsonResponse({
                'message': 'Error saving responses',
                'error': str(e)
            }, status=200)
    
    print("Rendering questionnaire.html for non-AJAX or GET request")
    return render(request, 'questionnaire.html')



# from django.contrib.auth import authenticate, login
# from django.shortcuts import render, redirect
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework import status
# from .models import User, Reminder
# from .serializers import UserSerializer
# from rest_framework.parsers import JSONParser, FormParser
# from django.contrib.auth.decorators import login_required
# import speech_recognition as sr
# import pyttsx3
# import dateparser
# from datetime import datetime, timedelta
# from celery import shared_task
# from django_celery_beat.models import PeriodicTask, CrontabSchedule
# import json
# from django.http import HttpResponse, JsonResponse
# import threading

# # Initialize speech recognition and TTS with a lock
# listener = sr.Recognizer()
# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[1].id)
# speech_lock = threading.Lock()  # Lock to synchronize speech

# listener.dynamic_energy_threshold = True
# listener.energy_threshold = 300
# listener.pause_threshold = 0.8
# listener.phrase_time_limit = 8
# listener.non_speaking_duration = 0.5

# def talk(text):
#     with speech_lock:  # Ensure only one speech at a time
#         engine.say(text)
#         engine.runAndWait()

# def take_command(prompt, expected_type="text"):
#     while True:
#         talk(prompt)
#         print(prompt)
#         try:
#             with sr.Microphone() as source:
#                 listener.adjust_for_ambient_noise(source, duration=2)
#                 print("Listening...")
#                 voice = listener.listen(source)
#                 command = listener.recognize_google(voice, language='en-US').lower()
#                 print(f"User said: {command}")

#                 if expected_type == "time":
#                     parsed = dateparser.parse(command, settings={'TIMEZONE': 'UTC'})
#                     return parsed.time() if parsed else None
#                 elif expected_type == "date":
#                     parsed = dateparser.parse(command, settings={'PREFER_DATES_FROM': 'future'})
#                     return parsed.date() if parsed else None
#                 elif expected_type == "text":
#                     return command
#         except sr.UnknownValueError:
#             talk("Sorry, I didn't catch that. Please repeat.")
#         except Exception as e:
#             print(f"Error: {e}")
#         talk("Please try again.")

# class RegisterView(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({'error': 'User not registered'}, status=status.HTTP_400_BAD_REQUEST)

#         if not user.check_password(password):
#             return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

#         if user.status != 'Active':
#             return Response({'error': 'Account is inactive'}, status=status.HTTP_400_BAD_REQUEST)

#         login(request, user)
#         return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)

# def Login_view(request):
#     return render(request, 'Login.html')

# def Register_view(request):
#     return render(request, 'Register.html')

# def splashscreen(request):
#     return render(request, 'splashscreen.html')

# @login_required
# def create_reminder(request):
#     if request.method == "POST":
#         task = request.POST.get('task')
#         task_time_str = request.POST.get('task_time')
#         task_date_str = request.POST.get('task_date')
#         reminder_type = request.POST.get('reminder_type')

#         try:
#             task_time = datetime.strptime(task_time_str, '%H:%M:%S').time()
#         except ValueError:
#             task_time = dateparser.parse(task_time_str).time() if task_time_str else None

#         task_date = datetime.strptime(task_date_str, '%Y-%m-%d').date() if task_date_str else None

#         if not task_time or not task_date:
#             return render(request, 'create_reminder.html', {
#                 'error': 'Invalid time or date format. Please try again.',
#                 'task': task, 'task_time': task_time_str, 'task_date': task_date_str, 'reminder_type': reminder_type
#             })

#         reminder = Reminder.objects.create(
#             user=request.user,
#             task=task,
#             task_time=task_time,
#             task_date=task_date,
#             reminder_type=reminder_type
#         )

#         schedule_reminder(reminder)
#         return JsonResponse({'message': 'Reminder set successfully', 'reminder_id': reminder.id})

#     task = take_command("Hey, what's the task?", "text")
#     task_time = take_command("At what time should I remind you?", "time")
#     task_date = take_command("On which date should I remind you?", "date")
#     reminder_type = take_command("Should I remind you once or daily?", "text")

#     confirmation = f"Reminder set for '{task}' on {task_date.strftime('%B %d')} at {task_time.strftime('%I:%M %p')}, {reminder_type}."
#     talk(confirmation)

#     task_time_str = task_time.strftime('%H:%M:%S')
#     task_date_str = task_date.strftime('%Y-%m-%d')

#     return render(request, 'create_reminder.html', {
#         'task': task, 'task_time': task_time_str, 'task_date': task_date_str, 'reminder_type': reminder_type
#     })

# @shared_task
# def play_ringtone(reminder_id):
#     from playsound import playsound
#     reminder = Reminder.objects.get(id=reminder_id)
#     playsound('static\images\marco.mp3')  # Replace with your ringtone file path
#     # Note: Popup logic will be handled client-side or via a desktop client
#     reminder.is_completed = True
#     reminder.save()

# def schedule_reminder(reminder):
#     schedule, _ = CrontabSchedule.objects.get_or_create(
#         minute=reminder.task_time.minute,
#         hour=reminder.task_time.hour,
#         day_of_month=reminder.task_date.day,
#         month_of_year=reminder.task_date.month,
#     )
#     PeriodicTask.objects.create(
#         crontab=schedule,
#         name=f'reminder-{reminder.id}',
#         task='RemindHer_app.views.play_ringtone',
#         args=json.dumps([reminder.id]),
#         one_off=reminder.reminder_type == 'Once'
#     )

# @login_required
# def snooze_reminder(request, reminder_id, minutes):
#     reminder = Reminder.objects.get(id=reminder_id, user=request.user)
#     new_time = (datetime.combine(reminder.task_date, reminder.task_time) + timedelta(minutes=minutes)).time()
#     reminder.task_time = new_time
#     reminder.is_completed = False
#     reminder.save()
#     schedule_reminder(reminder)
#     return JsonResponse({'message': 'Reminder snoozed'})

# @login_required
# def cancel_reminder(request, reminder_id):
#     reminder = Reminder.objects.get(id=reminder_id, user=request.user)
#     reminder.is_completed = True
#     reminder.save()
#     PeriodicTask.objects.filter(name=f'reminder-{reminder.id}').delete()
#     return JsonResponse({'message': 'Reminder canceled'})

# @login_required
# def check_reminders(request):
#     now = datetime.now()
#     reminders = Reminder.objects.filter(
#         user=request.user,
#         task_date=now.date(),
#         task_time__hour=now.hour,
#         task_time__minute=now.minute,
#         is_completed=False
#     )
#     if reminders.exists():
#         reminder = reminders.first()
#         return JsonResponse({
#             'reminder': {'id': reminder.id, 'task': reminder.task}
#         })
#     return JsonResponse({'reminder': None})

