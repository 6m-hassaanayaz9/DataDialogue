from django.db import models
    
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255, default=None, blank=True, null=True)
    refresh_token = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __str__(self):
        model_name = self.__class__.__name__
        fields_str = ", ".join((f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields))
        return f"{model_name}({fields_str})"


class Database(models.Model):
    database_id = models.AutoField(primary_key=True)
    database_name = models.CharField(max_length=255)
    access_key = models.CharField(max_length=255, blank=True, null=True)
    connection_string = models.CharField(max_length=255)

    def __str__(self):
        model_name = self.__class__.__name__
        fields_str = ", ".join((f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields))
        return f"{model_name}({fields_str})"

# class AccessList(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     database = models.ForeignKey(Database, on_delete=models.CASCADE)
#     class Meta:
#         unique_together = (('user', 'database'),)

class Conversation(models.Model):
    conversation_id = models.AutoField(primary_key=True)
    name = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    database = models.ForeignKey(Database, on_delete=models.CASCADE)

    def __str__(self):
        model_name = self.__class__.__name__
        fields_str = ", ".join((f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields))
        return f"{model_name}({fields_str})"

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        model_name = self.__class__.__name__
        fields_str = ", ".join((f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields))
        return f"{model_name}({fields_str})"

class Prompt(models.Model):
    prompt_id = models.AutoField(primary_key=True)
    prompt_data = models.TextField()
    database = models.ForeignKey(Database, on_delete=models.CASCADE)

    def __str__(self):
        model_name = self.__class__.__name__
        fields_str = ", ".join((f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields))
        return f"{model_name}({fields_str})"
