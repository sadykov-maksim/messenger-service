from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(GPTConnectorSettings)
class GPTConnectorSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек API."""
    list_display = ("model_name", "is_active", "token_limit", "tokens_used", "tokens_remaining")
    list_filter = ("is_active",)
    search_fields = ("model_name", "api_key")

    def tokens_remaining(self, obj):
        return obj.tokens_remaining
    tokens_remaining.short_description = "Остаток токенов"

class ChatResponseInline(admin.TabularInline):
    model = ChatResponse
    extra = 0

@admin.register(ChatRequest)
class ChatRequestAdmin(admin.ModelAdmin):
    """Админка для логов запросов."""
    list_display = ("id", "created_at", "user_input", "model_name")
    list_filter = ("created_at", "model_name")
    search_fields = ("user_input", "model_name", "api_key_used")
    ordering = ("-created_at",)
    inlines = [ChatResponseInline]


@admin.register(ChatResponse)
class ChatResponseAdmin(admin.ModelAdmin):
    """Админка для логов ответов."""
    list_display = ("id", "request", "created_at")
    list_filter = ("created_at",)
    search_fields = ("response_content",)
    ordering = ("-created_at",)


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    """Админка для истории чатов."""
    list_display = ("user_id", "message_role", "timestamp")
    list_filter = ("timestamp", "message_role")
    search_fields = ("user_id", "message_content")
    ordering = ("-timestamp",)
