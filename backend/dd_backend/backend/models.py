from django.db import models
    
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    access_token = models.JSONField(default=None, blank=True, null=True)
    refresh_token = models.JSONField(default=None, blank=True, null=True)


class Database(models.Model):
    database_id = models.AutoField(primary_key=True)
    database_name = models.CharField(max_length=255)
    access_key = models.CharField(max_length=255, blank=True, null=True)
    connection_string = models.CharField(max_length=255)

class AccessList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = (('user', 'database'),)

class Conversation(models.Model):
    conversation_id = models.AutoField(primary_key=True)
    name = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    database = models.ForeignKey(Database, on_delete=models.CASCADE)

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(default=None, blank=True, null=True)
    time_stamp = models.DateTimeField(auto_now_add=True)
    is_tabular = models.BooleanField(default=False)  # Boolean field for is_tabular
    headers = models.JSONField(default=list, null=True, blank=True)
    tableData = models.JSONField(default=list, null=True, blank=True) 

class Prompt(models.Model):
    prompt_id = models.AutoField(primary_key=True)
    prompt_data = models.TextField()
    database = models.ForeignKey(Database, on_delete=models.CASCADE)