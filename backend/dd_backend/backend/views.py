from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse


from django.core.exceptions import ObjectDoesNotExist


from django.views.decorators.csrf import csrf_exempt


from django.utils.decorators import method_decorator


from django.views import View


from django.contrib.auth.hashers import check_password, make_password



from .models import User


import jwt


from datetime import datetime, timedelta



@method_decorator(csrf_exempt, name='dispatch')

class LoginView(View):


    def post(self, request):


        # Assuming data is coming in JSON format and contains email and password
        

        data = request.POST  # If your data is coming in form data


        email = data.get('email')


        password = data.get('password')

        print("Data received:", data)  # Check if data is received correctly

        email = data.get('email')
        
        

        print("Email extracted:", email)  # Check the extracted email

        print("Password extracted:", password)  # Check the extracted password
        

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
        
        # Return response
        return JsonResponse({


            "status": 200,


            "message": "User logged in",


            "data": {


                "name": user.username,  # Assuming there's a 'name' field in your Admin model


                "tokens": tokens


            }


        })


    def get_tokens(self, user_id, email):

            #ASK HOW TO CHECK THE TIME IF IT IS EXPIRED AND WHEN SHARR WE GENERATE NEW TOKEN
        refresh_token = self.generate_token(user_id, email, token_type='refresh')



        # Generate access token with expiration time of 15 minutes


        access_token = self.generate_token(user_id, email, token_type='access')



        return {'refresh_token': refresh_token, 'access_token': access_token}
    


    def generate_token(self, user_id, email, token_type):


        # Define expiration time based on token type


        if token_type == 'refresh':


            expiry_time = datetime.utcnow() + timedelta(days=1)  # Refresh token expires in 1 day


        elif token_type == 'access':


            expiry_time = datetime.utcnow() + timedelta(minutes=15)  # Access token expires in 15 minutes


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


        # Implement logic to update refresh token in database


        # DB mein refresh and access token store karna hai and in seperate table?


        try:


            # Retrieve the user record from the database


            user = User.objects.get(user_id=user_id)


            user.access_token = access_token


            user.save()


        except User.DoesNotExist:


                # Handle case where user does not exist


            return JsonResponse({"status": 400, "message": "User not found"}, status=400)    
        pass
    



    def update_refresh_token(self, user_id, refresh_token):


            # Implement logic to update refresh token in database


            # DB mein refresh and access token store karna hai and in seperate table?


            try:


            # Retrieve the user record from the database


                user = User.objects.get(user_id=user_id)


                user.refresh_token = refresh_token


                user.save()


            except User.DoesNotExist:


                # Handle case where user does not exist


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
