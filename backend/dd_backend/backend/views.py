from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse


from django.core.exceptions import ObjectDoesNotExist


from django.views.decorators.csrf import csrf_exempt


from django.utils.decorators import method_decorator


from django.views import View


from django.contrib.auth.hashers import check_password, make_password

import base64




from .models import User
from .models import Database,Conversation,Message,AccessList
import requests
import time

import json
import ast

import jwt


from datetime import datetime, timedelta

BASE_URL = "http://localhost:12345"

@method_decorator(csrf_exempt, name='dispatch')
class AccessPrivateDatabase(View):
    def post(self, request):
        data = request.POST
        access_key = data.get('access_key')
        user_id = data.get("user_id")
        present_databases = data.get('present_databases').split(",")
        print("Received ", access_key,user_id, "present received :::: " , present_databases ) 
        database = []
        try:
            if(access_key.strip()=='0'):
                raise Database.DoesNotExist
            database_objects = Database.objects.get(access_key=access_key)
        except Database.DoesNotExist:
            return JsonResponse({'name': 'invalid'})
        
        if database_objects.database_name in present_databases:
            return JsonResponse({'name': 'already'})
        user = User.objects.get(user_id=user_id)
        access_entry = AccessList(user=user, database=database_objects)
        access_entry.save()
        return JsonResponse({'name': database_objects.database_name})


     

@method_decorator(csrf_exempt, name='dispatch')
class GetDatabaseNames(View):
    def post(self,request):
        data = request.POST
        user_id = data.get('user_id')
        print("user id is <LLLLLLL  " ,user_id)
        public_databases_objects = Database.objects.filter(access_key = 0)
        public_databases = [database.database_name for database in public_databases_objects]
        print(public_databases)
        user = User.objects.get(user_id=user_id)
        private_databases = []
        access_entries = AccessList.objects.filter(user=user)
        if access_entries is not None:
             private_databases = [entry.database.database_name for entry in access_entries]
        database_names = list(public_databases) + list(private_databases)
        print(database_names)
        return JsonResponse({'database_names': database_names})



@method_decorator(csrf_exempt, name='dispatch')
class SaveMessage(View):
    def post(self, request):
        data = request.POST
        query = data.get('query')
        answer = data.get('response')
        conversation_id = data.get('conversationId')
        print("Received ", query, answer, conversation_id)
        tableData = data.get('tableData')
        try:
            
            tableData=json.loads(tableData)
            print("Table data received::;;;", tableData)
        except:
            pass
        # tableData= ast.literal_eval(tableData)
        print("Table data astttttttttttt", tableData)
        is_tabular=data.get('is_tabular')
        if is_tabular.strip().lower() == 'true':
           is_tabular = True
        else:
            is_tabular = False
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        message = Message(question=query, answer = answer, conversation= conversation, is_tabular=is_tabular, headers=data.get('headers'), tableData=tableData)
        message.save()
        return JsonResponse({'status': 200, 'message': 'Message saved successfully'})





@method_decorator(csrf_exempt, name='dispatch')
class CreateConversation(View):
    def post(self, request):
        data = request.POST
        username = data.get('username')
        database_name = data.get('database')
        conversation_name = data.get('name')
        print("Received ", username, database_name, conversation_name)
        user = User.objects.get(username=username)
        database = Database.objects.get(database_name=database_name)
        conversation = Conversation(name=conversation_name, user=user, database=database)
        conversation.save()
        conversation_id = conversation.conversation_id
        print("sending back conversation id", conversation_id)
        return JsonResponse({'id': conversation_id,'name': conversation_name})



@method_decorator(csrf_exempt, name='dispatch')
class LoadPreviousView(View):
    def post(self, request):
        data = request.POST
        conversation_id = int(data.get('id'))
        conversation_name = data.get('name')
        print(conversation_id, conversation_name)
        conversation = Conversation.objects.get(conversation_id=conversation_id,name=conversation_name)
        print(conversation)
        messages = Message.objects.filter(conversation=conversation)
        
        

        message_data = []
        for message in messages:
            try:
                tableData=message.tableData['tableData']
            except:
                tableData = ''
            
            message_data.append({
                'question': message.question,
                'answer': message.answer,
                'is_tabular': message.is_tabular,
                'headers': message.headers.split(","),
                'tableData': tableData
               
            })
        print(message_data)
        # # Return the chat history as JSON response
        return JsonResponse({'messages': message_data}) 

@method_decorator(csrf_exempt, name='dispatch')
class ConversationsView(View):
    def post(self, request):
        data = request.POST
        username = data.get('username')
        database_name = data.get('database')
        print("Received ", username, database_name)
        conversations = Conversation.objects.filter(user__username=username, database__database_name=database_name)
        conversation_dict = {conversation.conversation_id: conversation.name for conversation in conversations}
        print(conversation_dict)
        return JsonResponse({'conversations': conversation_dict})



@method_decorator(csrf_exempt, name='dispatch')
class QueryView(View):

    def post(self, request):
        data = request.POST
        query = data.get('query')
        print("Received ", query)
        database_name= data.get('database')
        print("Database name received:", database_name)
        user_id= data.get('user_id')
        time.sleep(2)
        print("Query received:", query)
        reply = self.answer(query, database_name, user_id)
        print ("Replyyyyy:", reply)
        if(reply['is_tabular']):
            return JsonResponse({'status': 200, 'message': reply['answer'], 'remaining': reply['remaining'], 'headers': reply['headers'], 'is_tabular': reply["is_tabular"]})
        
            print ("Answerrrrrr:", reply['answer'])
            print ("Remainingggggg:", reply['remaining'])
        else:
            return JsonResponse({'status': 200, 'message': reply['answer'], 'remaining': reply['remaining'], 'is_tabular': reply["is_tabular"]})
    
    def answer(self, query, database_name, user_id):
        url = BASE_URL
        params = {'auth': '123', 'question': query, 'database': database_name, 'user_id': user_id }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            rem_len = response.json()['remaining']
            answer = response.json()['answer']        
            headers = response.json()['headers']
            is_tabular = response.json()['is_tabular']
            is_image = response.json()['is_image']
            
            if is_image:
                image_path = response.json()['image_path']
                
                
                image_content = requests.get(url+"/get-image",params = {'auth': '123','image_path':image_path})
                
                image = base64.b64encode(image_content.content).decode('utf-8')
            else:
                image = None

            if isinstance(answer, str):
                answer_list = answer.split('\n')
                reply = {
                    "answer": answer_list,
                    "remaining": rem_len,
                    "is_tabular": is_tabular,
                    "headers": headers,
                    "is_image": is_image,
                    "image": image
                }
                return reply

            reply = {
                "answer": answer,
                "remaining": rem_len,
                "is_tabular": is_tabular,
                "headers": headers,
                "is_image": is_image,
                "image": image
            }
            return reply
        else:
            return {"answer": "Error in fetching data", "remaining": 0, "is_tabular": False, "headers": []}


@method_decorator(csrf_exempt, name='dispatch')
class GenerateMoreData(View):
    def post(self, request):
        data = request.POST
        database_name = data.get('database_name')
        print("Database ", database_name)
        user_id= data.get('user_id')
        time.sleep(2)
        
        url = f'{BASE_URL}/generate-more'
        
        params = {'auth': '123', 'database': database_name, 'user_id': user_id}
        
        response = requests.get(url, params=params)

        
        if response.status_code == 200:
            print("responseDARAAaaaa",response.json())
            print("responseDARAAaaaa Data>>>>>>>>>>>>",response.json()['data'])
            if(response.json()['is_tabular']):
                return JsonResponse({'status': 200, 'message':response.json()['data'], 'remaining': response.json()['remaining'], 'headers': response.json()['headers'], 'is_tabular': response.json()['is_tabular']})
            else:
                return JsonResponse({'status': 200, 'message': response.json()['data'], 'remaining': response.json()['remaining'], 'is_tabular': response.json()['is_tabular']})
            
        else:
            print("Error:", response.status_code)
            return "Error in fetching data"




@method_decorator(csrf_exempt, name='dispatch')

class LoginView(View):


    def post(self, request):

        # Assuming data is coming in JSON format and contains email and password

        data = request.POST  # If your data is coming in form data


        email = data.get('email')


        password = data.get('password')

       
        try:
            # Check if user exists in the database
            print ("In try:", email)
            user = User.objects.get(email=email)
            print("User details:", user)  # Print user details
            print("User password from table", user.password)  # Print user password from table
            # Check if password is correct

            if not check_password(password, user.password):

                print("Invalid password")

                return JsonResponse({"status": 400, "message": "Invalid credentials"}, status=400)

            print("User found")

        except ObjectDoesNotExist:

            print("User not found")

            return JsonResponse({"status": 400, "message": "User not found"}, status=400)

        # If user exists and password is correct, generate tokens

        print("get token fun called")
        tokens = self.get_tokens(user.user_id, user.email)  # You need to implement this method

        print("Tokens generated:", tokens)  # Check the generated tokens
        self.update_access_token(user.user_id, tokens['access_token'])
        print("Access token updated")

        self.update_refresh_token(user.user_id, tokens['refresh_token'])
        print("Refresh token updated")

        print("User found")
        print("User id that has been sent is:", user.user_id)
        print("User name that has been sent is:", user.username)
        print("Access token that has been sent is:", tokens["access_token"])
        print("Refresh token that has been sent is:", tokens["refresh_token"])
        ##-----------------------------------------------------------------------
        
        url = f'{BASE_URL}/login'
        
        params = {'auth': '123', 'user_id': user.user_id, }
        response = requests.post(url, params=params)
        
        if not response.json()['status'] :
            print("Error in fetching data during llm Login")
            return JsonResponse({"status": 400, "message": "Error in fetching data during llm Login"}, status=400)
        
        
        ##-----------------------------------------------------------------------
        # Return response
        return JsonResponse({

            "status": 200,
            "message": "User logged in",
            "data": {

                "username": user.username, 
                "user_id": user.user_id,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                
                
            }

        })


    def get_tokens(self, user_id, email):

            #ASK HOW TO CHECK THE TIME IF IT IS EXPIRED AND WHEN SHARR WE GENERATE NEW TOKEN
        refresh_token = self.generate_token(user_id, email, token_type='refresh')



        # Generate access token with expiration time of 15 minutes


        access_token = self.generate_token(user_id, email, token_type='access')



        return {'refresh_token': refresh_token, 'access_token': access_token}
    
    def get_access_token(self, user_id, email):
            
            access_token = self.generate_token(user_id, email, token_type='access')
    
            return access_token
    def get_refresh_token(self, user_id, email):
                
                refresh_token = self.generate_token(user_id, email, token_type='refresh')
        
                return refresh_token
            
    def generate_token(self, user_id, email, token_type):


        # Define expiration time based on token type
        if token_type == 'refresh':
            expiry_time = datetime.utcnow() + timedelta(days=3)  # Refresh token expires in 1 day
        elif token_type == 'access':
            expiry_time = datetime.utcnow() + timedelta(days=1)  # Access token expires in 15 minutes
        else:
            raise ValueError("Invalid token type")
        # Create payload for the token

        token_payload = {

            'user_id': user_id,
            'email': email,
            'token_type': token_type,
            'exp': expiry_time

        }
        # Encode token using JWT with a secret key
        secret_key = 'Ah@m649'
        token = jwt.encode(token_payload, secret_key, algorithm='HS256')
        return token
    
    def update_access_token(self, user_id, access_token):

        try:


            user = User.objects.get(user_id=user_id)
            user.access_token = {"token": access_token, "expiry": (datetime.utcnow() + timedelta(days=1)).isoformat()}
            user.save()


        except User.DoesNotExist:
                # Handle case where user does not exist
            return JsonResponse({"status": 400, "message": "User not found"}, status=400)    
        pass
    



    def update_refresh_token(self, user_id, refresh_token):


            try:

                user = User.objects.get(user_id=user_id)


                user.refresh_token = {"token": refresh_token, "expiry": (datetime.utcnow() + timedelta(days=3)).isoformat()}


                user.save()


            except User.DoesNotExist:

                return JsonResponse({"status": 400, "message": "User not found"}, status=400)    
                pass
   

@method_decorator(csrf_exempt, name='dispatch')         

class SignupView(View):

        print("In SignupView")

        def post(self, request):
    

            data = request.POST  # If your data is coming in form data
    

            email = data.get('email')
    

            password = data.get('password')
    

            name = data.get('name')
    

            # Check if user already exists

            try:

                if User.objects.filter(email=email).exists():
        

                    return JsonResponse({"status": 400, "message": "User already exists"}, status=400)
        

                # Create user
                hashed_password = make_password(password)

                user = User(email=email, password=hashed_password, username=name , access_token="", refresh_token="")
                user.save()
        

                return JsonResponse({"status": 200, "message": "User created successfully"}, status=200)

            except Exception as e:

                print("Error in signup:", e)

                return JsonResponse({"status": 400, "message": "Error in signup"}, status=400)    


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def post(self, request):
 
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            print("Now the user id coming from frontend is:", user_id)
        
            if user_id is None:
                raise ValueError("User ID not found in request data")
             
            user = User.objects.get(user_id=user_id)
            user.access_token = ""
            user.refresh_token = ""
            user.save()
            print("User logged out")
            #------------------------------------
            url = f'{BASE_URL}/logout'
        
            params = {'auth': '123', 'user_id': user.user_id, }
            response = requests.post(url, params=params)
            if not response.json()['status'] :
                print("Error in fetching data during llm Logout")
                return JsonResponse({"status": 400, "message": "Error in fetching data during llm Logout"}, status=400)
            #------------------------------------
            return JsonResponse({"status": 200, "message": "User logged out successfully"}, status=200)

        except User.DoesNotExist:
            print("User not found")
            return JsonResponse({"status": 400, "message": "User not found"}, status=400)
        
                        

@method_decorator(csrf_exempt, name='dispatch')  
class validateToken(View):
    login_view = LoginView()
    def post(self, request):
        data = json.loads(request.body)
        print("Data received in Validate Token:>>>", data)
        user_id= data.get('user_id')
        access_token = data.get('access_token')
        print("Access token received:", access_token)
        refresh_token = data.get('refresh_token')
        print("Refresh token received:", refresh_token)
        user = User.objects.get(user_id=user_id)
        print("User details------------->:", user)
        print("User access token------------->:", user.access_token["token"])
        print("User access token------------->:", user.access_token["expiry"])
        print("User refresh token------------->:", user.refresh_token["token"])
        print("User refresh token------------->:", user.refresh_token["expiry"])
        if user.access_token["token"]== access_token and user.refresh_token["token"]== refresh_token:            
            print("Token is valid")
            if user.access_token["expiry"] < datetime.utcnow().isoformat():
                
                
                print("Access token is expired")
                new_access_token = self.login_view.get_access_token(user_id, user.email)
                #------------------------------------------------ye check karo ki new access token generate ho raha hai ya nahi
                print("New access token generated:", new_access_token)
                self.login_view.update_access_token(user_id, new_access_token)
                print("Access token updated")
                return JsonResponse({"status": 201, "message": "New access token created", "new_access_token": new_access_token}, status=201)
            
            
            elif user.refresh_token["expiry"] < datetime.utcnow().isoformat():
                print("Refresh token is expired")
                
                return JsonResponse({"status": 400, "message": "Refresh Token is invalid"}, status=200)
            
            
            else:
                print("Tokens are valid")
                return JsonResponse({"status": 200, "message": "Token is valid"}, status=200)
                
        
        else:
            print(" Tokens are invalid")
            return JsonResponse({"status": 400, "message": "Session expired Login again"}, status=400)
        

@method_decorator(csrf_exempt, name='dispatch')
class GetUserTableView(View):
    def get(self, request):
        try:
            # Retrieve all user records
            users = User.objects.all()
            # Serialize the data
            serialized_data = [{'username': usr.username, 'email': usr.email} for usr in users]
            
            # Return the serialized data as JSON response
            return JsonResponse({'status': 200, 'data': serialized_data})
        except Exception as e:
            # Handle any exceptions and return an error response
            return JsonResponse({'status': 500, 'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GetDatabaseTableView(View):
    def get(self, request):
        try:
            # Retrieve all database records
            databases = Database.objects.all()
            # Serialize the data
            serialized_data = [{'database_name': db.database_name, 'access_key': db.access_key} for db in databases]
            
            # Return the serialized data as JSON response
            return JsonResponse({'status': 200, 'data': serialized_data})
        except Exception as e:
            # Handle any exceptions and return an error response
            return JsonResponse({'status': 500, 'error': str(e)}, status=500)







# @method_decorator(csrf_exempt, name='dispatch')
# class GetDatabaseTableView(View):
#     def get(self, request):
#         try:
#             # Retrieve all database records
#             databases = Database.objects.all()
#             # Serialize the data
#             serialized_data = [{'database_name': db.database_name, 'access_key': db.access_key} for db in databases]
                        
#             # Return the serialized data as JSON response
#             return JsonResponse({'status': 200, 'data': serialized_data})
#         except Exception as e:
#             # Handle any exceptions and return an error response
#             return JsonResponse({'status': 500, 'error': str(e)}, status=500)
        
# @method_decorator(csrf_exempt, name='dispatch')
# class GetUserTableView(View):
#     def get(self, request):
#         try:
#             # Retrieve all database records
#             user = User.objects.all()
#             # Serialize the data
#             serialized_data = [{'username': usr.username, 'email': usr.email} for usr in user]
                        
#             # Return the serialized data as JSON response
#             return JsonResponse({'status': 200, 'data': serialized_data})
#         except Exception as e:
#             # Handle any exceptions and return an error response
#             return JsonResponse({'status': 500, 'error': str(e)}, status=500)        


        
@method_decorator(csrf_exempt, name='dispatch') 
class UpdateAccess(View):
    def post(self, request):
        data = request.POST
        database_name = data.get('database_name')
        updated_access_key = data.get('access_key')
        print("Received ", database_name, updated_access_key)
        
        database =  Database.objects.get(database_name=database_name)
        database.access_key=updated_access_key
        database.save()
        print("Access key updated")
        
        return JsonResponse({'status': 200, 'message': 'Message saved successfully'})

@method_decorator(csrf_exempt, name='dispatch') 
class Deldb(View):
    def post(self, request):
        try:
            data = request.POST
            database_name = data.get('database_name')

            print("Received ", database_name)
            
            database =  Database.objects.get(database_name=database_name)
            
            database.delete()

            return JsonResponse({'status': 200, 'message': 'Database deleted successfully'})
        except Database.DoesNotExist:
            return JsonResponse({'status': 404, 'message': 'Database not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})



        
        
        

@method_decorator(csrf_exempt, name='dispatch')
class Deluser(View):
    def post(self, request):
        try:
            data = request.POST
            username = data.get('username')

            print("Received ", username)
            
            user =  User.objects.get(username=username)
            
            user.delete()

            return JsonResponse({'status': 200, 'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 404, 'message': 'User not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

