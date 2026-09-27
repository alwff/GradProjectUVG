import os

import resend


def send_email(
    recipients,
    subject,
    html
):

    api_key = os.environ.get(
        "RESEND_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "RESEND_API_KEY no está configurada."
        )

    resend.api_key = api_key

    params = {
        "from": (
            "Sistema de Colecciones "
            "<onboarding@resend.dev>"
        ),
        "to": recipients,
        "subject": subject,
        "html": html
    }

    return resend.Emails.send(
        params
    )