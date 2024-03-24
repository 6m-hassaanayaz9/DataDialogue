from django.contrib import admin
from .models import User, Database, Conversation, Message, Prompt
# Register your models here.
admin.site.register(User)
admin.site.register(Database)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Prompt)
# Compare this snippet from datadialgue_bckend/auth/views.py:
from django.views import View
