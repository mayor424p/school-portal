import ssl
import certifi
from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False

        # Create a verified SSL context with certifi's trusted CA bundle
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.load_verify_locations(cafile=certifi.where())

        try:
            self.connection = self.connection_class(
                self.host,
                self.port,
                timeout=self.timeout,
            )
            self.connection.set_debuglevel(0)
            self.connection.ehlo()
            self.connection.starttls(context=self.ssl_context)
            self.connection.ehlo()

            if self.username and self.password:
                self.connection.login(self.username, self.password)

            return True
        except Exception as e:
            if not self.fail_silently:
                raise
