from django.contrib import admin
from django.core.mail import send_mail
from django.core.mail import EmailMessage

from .models import *

# Register your models here.
@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'created_at', 'updated_at')
    search_fields = ('name', 'subject')

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('to_email', 'template', 'status', 'created_at', 'sent_at')
    list_filter = ('status',)
    search_fields = ('to_email', 'template__name')

@admin.register(EmailUser)
class EmailUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    filter_horizontal = ('users',)

@admin.register(ScheduledEmail)
class ScheduledEmailAdmin(admin.ModelAdmin):
    list_display = ('email_template', 'user_profile', 'cluster', 'scheduled_time', 'is_sent', 'created_at')
    list_filter = ('is_sent',)
    search_fields = ('email_template__name', 'user_profile__email', 'cluster__name')
    raw_id_fields = ('user_profile', 'cluster')
    actions = ['send_selected_newsletter']

    @admin.action(description="Отправить выбранные новостные рассылки")
    def send_selected_newsletter(self, request, queryset):
        for email in queryset.filter(is_sent=False):
            try:
                if email.cluster:
                    cluster = email.cluster.users.all()
                else:
                    cluster = [email.user_profile]

                smtp_profile = SMTPProfile.objects.filter(default=True).first()

                if not smtp_profile:
                    self.message_user(request, "Не найден профиль SMTP по умолчанию.", level="error")
                    continue

                for user_cluster in cluster:
                    context_data = {
                        'first_name': user_cluster.first_name,
                        'last_name': user_cluster.last_name,
                    }

                    email_body = email.email_template.render_body(context_data)

                    email_message = EmailMessage(
                        subject=email.email_template.subject,
                        body=email_body,
                        from_email=smtp_profile.username,
                        to=[user_cluster.email],
                        connection=smtp_profile.get_connection()
                    )
                    email_message.content_subtype = 'html'
                    email_message.send()

                email.is_sent = True
                email.save()
            except Exception as e:
                self.message_user(request, f"Ошибка: {e}", level="error")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('email_template', 'user_profile', 'cluster')

@admin.register(SMTPProfile)
class SMTPProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'username', 'use_tls', 'use_ssl', 'created_at', 'updated_at')
    search_fields = ('name', 'host', 'username')
    list_filter = ('use_tls', 'use_ssl')