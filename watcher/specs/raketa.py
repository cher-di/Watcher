import email.message

import requests

from watcher.specs import base


class Raketa(base.Spec):

    WATCHES_PAGE = 'https://raketa.com/product/raketa-russkij-kod-0286/'

    @classmethod
    def name(cls) -> str:
        return 'raketa'

    def reached_state(self) -> bool:
        resp = requests.get(self.WATCHES_PAGE)
        resp.raise_for_status()
        return 'Предзаказ временно закрыт' not in resp.text

    def render_email_message(self) -> email.message.EmailMessage:
        message = email.message.EmailMessage()
        message['Subject'] = 'Предзаказ на часы Ракета открыт'
        message.set_content(f'Оформить предзаказ: {self.WATCHES_PAGE}')
        return message
