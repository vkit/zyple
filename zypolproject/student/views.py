from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from .models import Userprofile,Task, AssignTask
from rest_framework.response import Response
import base64
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .utils import check_availibity
from .serializers import AddTaskSerializer, UpdateStatusSerializer, ApproveTaskSerializer, RegisterSerializer, LoginSerializer,AssignTaskSerializer

# This api  for user registrations

class Register(APIView):
    def post(self, request):
        try:
            data = request.POST
            serializer = RegisterSerializer(data=data)
            if not serializer.is_valid():
                print serializer.errors
                st = {'status': 'failure', 'message': 'invalid data'}
                return Response({'meta': st})
            email = data.get('email')
            password = base64.b64decode(data.get('password'))
            role = data.get('role')
            # check the availibility
            availability = check_availibity(username=data.get('email'))
            if availability:
                st = {'status': 'failure', 'message': 'username is already exists'}
                return Response({'meta': st}) 
            
            user = User.objects.create_user(username=email,password=password)
                
            userprofile = Userprofile.objects.create(user=user)
            # Generate the Token

            token,created = Token.objects.get_or_create(user=user)
            lis = list()
            if token:
                data = {'user_id':user.id,'email':email,'token':token.pk,'role':role}
                lis.append(data)
            st = {'status': 'success', 'message': 'registration succesfully'}
            return Response({'meta': st, 'register': lis})
        except Exception as e:
            print e

# Uer login api 
class Login(APIView):
    def post(self, request):
        try:
            data = request.POST
            serializer = LoginSerializer(data=data)
            if not serializer.is_valid():
                st = {'status': 'failure', 'message': 'invalid data'}
                return Response({'meta': st})
            email = data.get('email')
            password = base64.b64decode(data.get('password'))
            lis = list()
            availability = check_availibity(username=data.get('email'))
            if not availability:
                st = {'status': 'failure', 'message': 'email id is does not exists'}
                return Response({'meta': st}) 
            user = authenticate(username=email, password=password)
            if user is not None:
                token,created = Token.objects.get_or_create(user=user)
                user_detail = {
                    'token':token.pk, 
                    'user':user.username,
                    'user_id': user.id
                }
                lis.append(user_detail)
                st = {'status': 'success', 'message': 'login successfully'}
                return Response({'meta': st,'data':lis})
        except  Exception as e:
            print e

# Update user profile based on the role

class UpdateProfile(APIView):
    def get(self, request):
        try:
            user = request.user
            userprofile = Userprofile.objects.get(user=user)
            if userprofile.role == 3:
                userprofile.is_admin = True
                userprofile.save()
                st = {'status': 'success', 'message': 'userprofile updated succesfully'}
                return Response({'meta': st})
            elif userprofile.role == 2:
                userprofile.is_teacher = True
                userprofile.save()
                st = {'status': 'success', 'message': 'userprofile updated succesfully'}
                return Response({'meta': st})
            else:
                userprofile.is_student = True
                userprofile.save()
                st = {'status': 'success', 'message': 'userprofile updated succesfully'}
                return Response({'meta': st})
        except Exception as e:
            print e


# Only admin or teacher create the task
class CreateTask(APIView):
    def post(self, request):
        try:
            user = request.user
            data = request.POST
            serializer = AddTaskSerializer(data=data)
            if not serializer.is_valid():
                st = {'status': 'failure', 'message': 'invalid data'}
                return Response({'meta': st})
            lis=list()
            userprofile = Userprofile.objects.get(user=user)
            if userprofile.is_admin or userprofile.is_teacher:
                Task.objects.create(
                    task_headline = data.get('task_headline'),
                    task_body = data.get('task_body'),
                    user=user,
                )
                detail = {
                    'task_headline': data.get('task_headline'),
                    'task_body': data.get('task_body'),
                    'user': user.username,
                }
                lis.append(detail)
                st = {'status': 'success', 'message': 'task created succefully'}
                return Response({'meta': st, 'data': lis})
            else:
                st = {'status': 'failure', 'message': 'you are not admin or teacher to create the task'}
                return Response({'meta': st})
        except Exception as e:
            print e

    # Only admin can delete the task
    def delete(self, request, task_id):
        try:
            user = request.user
            userprofile = Userprofile.objects.get(user=user)
            if userprofile.is_admin:
                task=Task.objects.filter(pk=task_id, user=user)
                if task.exists():
                    task.delete()
                    st = {'status': 'succes', 'message': 'succesfully deleted'}
                    return Response({'meta':st})
                else:
                    st = {'status': 'failure', 'message': 'no task to delete'}
                    return Response({'meta':st})
            else:
                st = {'status': 'failure', 'message': 'you are not admin to delete this task'}
                return Response({'meta': st})
        except Exception as e:
            print e

# Now assign the task to students(ony admin or teacher can assign task to students)

class AssignTask(APIView):
    def post(self, request):
        try:
            data = request.POST
            user = request.user
            serializer = AssignTaskSerializer(data=data)
            if not serializer.is_valid():
                st = {'status': 'failure', 'message': 'invalid data'}
                return Response({'meta': st})
            task_instance = Task.objects.get(pk=data.get('task_id'))
            user_id = data.get('user_id')
            uid = User.objects.get(id=user_id)
            userprofile = Userprofile.objects.get(user=user)
            if userprofile.is_admin or userprofile.is_teacher:
                AssignTask.objects.create(
                    task=task_instance,
                    student_to=uid,
                    task_status=1
                )
                st = {'status': 'success', 'message': 'task created succefully'}
                return Response({'meta': st})
            else:
                st = {'status': 'failure', 'message': 'you are not admin or teacher to create the task'}
                return Response({'meta': st})
        except Exception as e:
            print e


# Students can see there task list
class TaskList(APIView):
    def get(self, request):
        try:
            user = request.user
            data = request.POST
            lis = []
            assigntasks=AssignTask.objects.filter(task_status=1)
            for assigntask in assigntasks:
                task_id = assigntask.id
                task_headline = assigntask.task.task_headline
                task_body = assigntask.task.task_body
                task_status = assigntask.task_status
                data_detail = {
                    'task_id': task_id,
                    'task_headline': task_headline,
                    'task_body': task_body,
                    'task_status': task_status
                } 
                lis.append(data_detail)
            st = {'status':'success', 'message': 'list of student task'}
            return Response({"meta": st, 'task_list': lis})
        except AssignTask.DoesNotExist:
            st = {'status': 'failure', 'message': 'task does not exists'}
            return Response({'meta':st})

# Student can update the status
class StudentUpdateStatus(APIView):
    def put(self, request):
        try:
            data = request.POST
            user = request.user
            serializer = ApproveTaskSerializer(data=data)
            if not serializer.is_valid():
                st = {'status': 'failure', 'message': 'invalid data'}
                return Response({'meta': st})
            task_instance = Task.objects.get(pk=data.get('task_id'))
            assign = AssignTask.objects.filter(task=task_instance, student_to=user)
            assign.task_status = data.get('status')
            assign.save()
            st = {'status': 'success', 'message': 'successfully updated the status'}
            return Response({'meta':st})
        except Task.DoesNotExist:
            st = {'status': 'success', 'message': 'invalid task'}
            return Response({'meta':st})


# only addmin or teacher can approve or disappprove the task(also make sure that student task status should be done)

class ApproveView(APIView):
    def post(self, request):
        try:
            data = request.POST
            user = request.user
            serializer = ApproveTaskSerializer(data=data)
            if not serializer.is_valid():
                st = {'status': 'failure', 'message': 'invalid data'}
                return Response({'meta': st})
            userprofile = Userprofile.objects.get(user=user)
            task_instance = Task.objects.get(pk=data.get('task_id'))
            if userprofile.is_admin or userprofile.is_teacher:
                if task_instance.assigntask_set.filter(task_status=6):
                    task_instance.assigntask_set.update(task_status=data.get('status'))
                    st = {'status': 'success', 'message': 'successfully updated the status'}
                    return Response({'meta':st})
                else:
                    st = {'status': 'failure', 'message': 'task is still in progres cant change the status'}
                    return Response({'meta':st})
            else:
                st = {'status': 'failure', 'message': 'you are not admin or teacher to create the task'}
        except Exception as e:
            print e
