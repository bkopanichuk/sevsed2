import asyncio
import smtplib

from django.conf import settings
from periodic import Periodic

from config.email_settings import EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL
from hash_checker.project_hash import CheckProjectHash


async def check_and_notificate():
    if await CheckProjectHash():
        mail_client = smtplib.SMTP(EMAIL_HOST)
        mail_client.starttls()
        mail_client.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        admins = settings.ADMINS

        for admin in admins:
            BODY = "\r\n".join((
                "From: %s" % DEFAULT_FROM_EMAIL,
                "To: %s" % admin[1],
                "Subject: %s" % "Warning",
                "",
                "Hash of the app has been changed, please update the app "
            ))

            mail_client.sendmail(DEFAULT_FROM_EMAIL, admin[1], BODY)
            print("send")

        mail_client.quit()



async def main():
    p = Periodic(3, check_and_notificate)
    await p.start()


loop = asyncio.get_event_loop()
task = loop.create_task(main())
loop.run_forever()
