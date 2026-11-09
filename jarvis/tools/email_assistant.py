import os
import smtplib
import imaplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any

class EmailTool:
    """
    Интеллектуальный почтовый секретарь Джарвиса:
    - Чтение последних входящих писем (Яндекс, Mail.ru, Gmail)
    - Поиск важных писем и их суммаризация
    - Отправка писем через SMTP
    """

    @staticmethod
    def get_credentials():
        email_user = os.getenv("EMAIL_USER", "")
        email_pass = os.getenv("EMAIL_PASS", "") # пароль приложения
        imap_server = os.getenv("EMAIL_IMAP", "imap.yandex.ru")
        smtp_server = os.getenv("EMAIL_SMTP", "smtp.yandex.ru")
        return email_user, email_pass, imap_server, smtp_server

    @staticmethod
    def check_inbox(limit: int = 5) -> str:
        """Проверить последние входящие письма"""
        user, pwd, imap_host, _ = EmailTool.get_credentials()
        if not user or not pwd:
            return "Сэр, почта еще не настроена. Укажите логин и пароль приложения в Настройках Почты."

        try:
            mail = imaplib.IMAP4_SSL(imap_host)
            mail.login(user, pwd)
            mail.select("inbox")

            status, messages = mail.search(None, "ALL")
            if status != "OK":
                return "Не удалось получить список писем, сэр."

            msg_ids = messages[0].split()
            if not msg_ids:
                return "Ваш почтовый ящик пуст, сэр."

            latest_ids = msg_ids[-limit:]
            latest_ids.reverse()

            results = []
            for m_id in latest_ids:
                res, data = mail.fetch(m_id, "(RFC822)")
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Тема
                subject, encoding = decode_header(msg["Subject"] or "Без темы")[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8", errors="ignore")

                # От кого
                from_, encoding = decode_header(msg.get("From") or "Неизвестный")[0]
                if isinstance(from_, bytes):
                    from_ = from_.decode(encoding or "utf-8", errors="ignore")

                date = msg.get("Date", "")
                results.append(f"• От: {from_}\n  Тема: {subject}\n  Дата: {date[:16]}")

            mail.close()
            mail.logout()
            return f"Вот последние входящие письма (всего проверено {len(results)}):\n\n" + "\n\n".join(results)
        except Exception as e:
            return f"Ошибка при подключении к почтовому серверу: {str(e)}"

    @staticmethod
    def send_email(to_email: str, subject: str, message_body: str) -> str:
        """Отправить письмо получателю"""
        user, pwd, _, smtp_host = EmailTool.get_credentials()
        if not user or not pwd:
            return "Сэр, почта не настроена. Укажите EMAIL_USER и EMAIL_PASS в настройках."

        try:
            msg = MIMEMultipart()
            msg["From"] = user
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(message_body, "plain", "utf-8"))

            server = smtplib.SMTP_SSL(smtp_host, 465)
            server.login(user, pwd)
            server.sendmail(user, to_email, msg.as_string())
            server.quit()
            return f"Письмо успешно отправлено адресату {to_email}, сэр."
        except Exception as e:
            return f"Не удалось отправить письмо: {str(e)}"
