from django.db import models

# Create your models here.
class GPTConnectorSettings(models.Model):
    """Настройки для подключения к Mistral API."""
    api_key = models.CharField(max_length=255, help_text="API ключ для доступа к Mistral API")
    model_name = models.CharField(max_length=255, default="mistral-large-latest", help_text="Имя модели для запросов")
    is_active = models.BooleanField(default=True, help_text="Флаг активности настройки")
    token_limit = models.IntegerField(default=100000, help_text="Общий лимит токенов")
    tokens_used = models.IntegerField(default=0, help_text="Количество использованных токенов")

    @property
    def tokens_remaining(self):
        return self.token_limit - self.tokens_used

    def __str__(self):
        return f"Settings for model {self.model_name}"


class ChatRequest(models.Model):
    """Лог запросов к API."""
    created_at = models.DateTimeField(auto_now_add=True, help_text="Дата и время создания запроса")
    user_input = models.TextField(help_text="Вопрос пользователя")
    model_name = models.CharField(max_length=255, help_text="Имя используемой модели")
    api_key_used = models.CharField(max_length=255, help_text="API ключ, использованный для запроса")

    def __str__(self):
        return f"Request at {self.created_at}: {self.user_input}"


class ChatResponse(models.Model):
    """Лог ответов от API."""
    request = models.OneToOneField(ChatRequest, on_delete=models.CASCADE, related_name="response", help_text="Связанный запрос")
    response_content = models.TextField(help_text="Ответ от модели")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Дата и время получения ответа")

    def __str__(self):
        return f"Response for Request {self.request.id}"


class ChatHistory(models.Model):
    """История чатов с пользователями."""
    user_id = models.CharField(max_length=255, help_text="Идентификатор пользователя")
    message_role = models.CharField(max_length=50, choices=[('user', 'User'), ('assistant', 'Assistant')], help_text="Роль отправителя")
    message_content = models.TextField(help_text="Содержание сообщения")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Время отправки сообщения")

    def __str__(self):
        return f"ChatHistory {self.user_id} at {self.timestamp}"