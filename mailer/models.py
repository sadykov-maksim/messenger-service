from django.core.mail.backends.smtp import EmailBackend

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.template import Context, Template
from django.template.loader import render_to_string

# Create your models here.
class EmailTemplate(models.Model):
    """
    Модель для хранения шаблонов электронных писем.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Имя шаблона",
                            help_text="Уникальное имя для шаблона письма.")
    subject = models.CharField(max_length=255, verbose_name="Тема", help_text="Тема письма.")
    body = models.TextField(verbose_name="Тело", help_text="HTML содержимое письма.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    def render_body(self, context):
        """
        Renders the body of the email with the context data.
        """
        template = Template(self.body)
        context = Context(context)
        return template.render(context)

    class Meta:
        verbose_name = _("Email Template")
        verbose_name_plural = _("Email Templates")
        db_table = "email_template"

    def __str__(self):
        return self.name

class Email(models.Model):
    """
    Модель для хранения информации о письмах, готовых к отправке или уже отправленных.
    """
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("sent", _("Sent")),
        ("failed", _("Failed")),
    ]

    to_email = models.EmailField(verbose_name="Получатель", help_text="Email адрес получателя.")
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, verbose_name='Шаблон письма')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Статус",
                              help_text="Статус письма.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Отправлено", help_text="Время отправки письма.")

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")
        db_table = "email"

    def __str__(self):
        return f"{self.template} -> {self.to_email}"

class EmailUser(models.Model):
    """
    Модель для хранения информации о пользователе, включая имя, фамилию и email.
    """

    first_name = models.CharField(max_length=100, verbose_name="Имя", help_text="Имя пользователя.", null=True,
                                  blank=True)
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", help_text="Фамилия пользователя.", null=True,
                                 blank=True)
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Email адрес пользователя.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = _("Email User")
        verbose_name_plural = _("Email Users")
        db_table = "email_user"

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

class Cluster(models.Model):
    """
    Модель для хранения групп пользователей.
    """
    name = models.CharField(max_length=100, verbose_name="Имя кластера", help_text="Имя группы пользователей.")
    users = models.ManyToManyField(EmailUser, verbose_name="Пользователи", help_text="Список пользователей в группе.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = _("Cluster")
        verbose_name_plural = _("Clusters")
        db_table = "cluster"

    def __str__(self):
        return self.name

class SMTPProfile(models.Model):
    """
    Модель для хранения SMTP профилей и настроек.
    """
    name = models.CharField(max_length=100, verbose_name="Имя профиля", help_text="Имя SMTP профиля.")
    host = models.CharField(max_length=255, verbose_name="Хост", help_text="SMTP хост.")
    port = models.PositiveIntegerField(verbose_name="Порт", help_text="SMTP порт.")
    username = models.CharField(max_length=255, verbose_name="Имя пользователя", help_text="SMTP имя пользователя.")
    password = models.CharField(max_length=255, verbose_name="Пароль", help_text="SMTP пароль.")
    use_tls = models.BooleanField(default=False, verbose_name="Использовать TLS", help_text="Использовать TLS для соединения.")
    use_ssl = models.BooleanField(default=False, verbose_name="Использовать SSL", help_text="Использовать SSL для соединения.")
    default = models.BooleanField(default=False, verbose_name="По умолчанию")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = _("SMTP Profile")
        verbose_name_plural = _("SMTP Profiles")
        db_table = "smtp_profile"

    def get_connection(self):
        return EmailBackend(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls,
            use_ssl=self.use_ssl,
        )

    def __str__(self):
        return self.name

class ScheduledEmail(models.Model):
    """
    Модель для хранения запланированных писем.
    """

    email_template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, verbose_name="Шаблон письма",
                                       help_text="Шаблон для использования в запланированном письме.")
    user_profile = models.ForeignKey(EmailUser, null=True, blank=True, on_delete=models.CASCADE,
                                     verbose_name="Профиль пользователя", help_text="Профиль пользователя, связанный с письмом.")
    cluster = models.ForeignKey(Cluster, null=True, blank=True, on_delete=models.CASCADE,
                                verbose_name="Кластер", help_text="Кластер пользователей, связанный с письмом.")
    scheduled_time = models.DateTimeField(verbose_name="Запланированное время",
                                          help_text="Время, когда письмо должно быть отправлено.")
    is_sent = models.BooleanField(default=False, verbose_name="Отправлено", help_text="Было ли письмо отправлено.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = _("Scheduled Email")
        verbose_name_plural = _("Scheduled Emails")
        db_table = "scheduled_email"

    def __str__(self):
        if self.user_profile:
            return f"{self.email_template.name} -> {self.user_profile}"
        elif self.cluster:
            return f"{self.email_template.name} -> {self.cluster}"
        else:
            return f"{self.email_template.name} -> No recipient"
