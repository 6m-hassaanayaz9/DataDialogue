from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.hashers import check_password
from .models import User
import jwt
from datetime import datetime, timedelta

@method_decorator(csrf_exempt, name='dispatch')
class SignInView(View):
    def post(self, request):
        # Assuming data is coming in JSON format and contains email and password
        data = request.POST  # If your data is coming in form data
        email = data.get('email')
        password = data.get('password')

        try:
            # Check if user exists
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            return JsonResponse({"status": 400, "message": "User not found"}, status=400)

        # Verify password
        if not check_password(password, user.password):
            return JsonResponse({"status": 400, "message": "Invalid credentials"}, status=400)
#---------------------------------------------------------
        # If user exists and password is correct, generate tokens
        tokens = self.get_tokens(user.id, user.email)  # You need to implement this method
        self.update_access_token(user.id, tokens['access_token'])
        self.update_refresh_token(user.id, tokens['refresh_token']) 
        
#---------------------------------------------------------
        # Return response
        return JsonResponse({
            "status": 200,
            "message": "User logged in",
            "data": {
                "name": user.username,  # Assuming there's a 'name' field in your Admin model
                "tokens": tokens
            }
        })

#---------------------------------------------------------

    def get_tokens(self, admin_id, admin_email):
            refresh_token = self.generate_token(admin_id, admin_email, token_type='refresh')

        # Generate access token with expiration time of 15 minutes
            access_token = self.generate_token(admin_id, admin_email, token_type='access')

            return {'refresh_token': refresh_token, 'access_token': access_token}
    
    def generate_token(self, admin_id, admin_email, token_type):
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

    def update_access_token(self, admin_id, acess_token):
            # Implement logic to update refresh token in database
            # DB mein refresh and access token store karna hai and in seperate table?
            try:
            # Retrieve the user record from the database
                user = User.objects.get(id=user_id)
                user.access_token = access_token
                user.save()
            except User.DoesNotExist:
                # Handle case where user does not exist
                return JsonResponse({"status": 400, "message": "User not found"}, status=400)    
                pass
    

    def update_refresh_token(self, admin_id, refresh_token):
            # Implement logic to update refresh token in database
            # DB mein refresh and access token store karna hai and in seperate table?
            try:
            # Retrieve the user record from the database
                user = User.objects.get(id=user_id)
                user.refresh_token = refresh_token
                user.save()
            except User.DoesNotExist:
                # Handle case where user does not exist
                return JsonResponse({"status": 400, "message": "User not found"}, status=400)    
                pass