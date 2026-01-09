from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

class WhatsAppService:
    def __init__(self):
        """
        Inicializa el servicio de WhatsApp usando Twilio.
        
        Necesitas en tu .env:
        - TWILIO_ACCOUNT_SID
        - TWILIO_AUTH_TOKEN
        - TWILIO_WHATSAPP_NUMBER
        """
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            raise ValueError("TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN son requeridos")
        
        self.client = Client(account_sid, auth_token)
        self.from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        print(f"📱 WhatsApp Service inicializado con Twilio")
        print(f"📞 Número: {self.from_number}")
    
    def send_message(self, to_number: str, message: str):
        """
        Envía un mensaje de WhatsApp usando Twilio.
        
        Args:
            to_number: Número del destinatario (puede incluir o no 'whatsapp:' al inicio)
            message: Contenido del mensaje
        
        Returns:
            Twilio Message object
        """
        # Asegurar formato whatsapp:
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'
        
        from_number = self.from_number
        if not from_number.startswith('whatsapp:'):
            from_number = f'whatsapp:{from_number}'
        
        try:
            message_obj = self.client.messages.create(
                from_=from_number,
                body=message,
                to=to_number
            )
            print(f"✅ Mensaje enviado a {to_number}: {message_obj.sid}")
            return message_obj
        except Exception as e:
            print(f"❌ Error enviando mensaje: {str(e)}")
            raise
