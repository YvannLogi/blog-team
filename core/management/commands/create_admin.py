import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Crée le superuser à partir des variables d'environnement "
        "ADMIN_PHONE, ADMIN_NAME et ADMIN_PASSWORD. "
        "Ne fait rien s'il existe déjà (on peut donc la lancer à chaque déploiement)."
    )

    def handle(self, *args, **options):
        phone = os.getenv("ADMIN_PHONE")
        name = os.getenv("ADMIN_NAME")
        password = os.getenv("ADMIN_PASSWORD")

        missing = [
            key for key, value in {
                "ADMIN_PHONE": phone,
                "ADMIN_NAME": name,
                "ADMIN_PASSWORD": password,
            }.items() if not value
        ]
        if missing:
            raise CommandError(f"Variables manquantes : {', '.join(missing)}")

        User = get_user_model()

        # On ne modifie jamais un admin existant : si tu changes son mot de passe
        # depuis l'admin, un nouveau déploiement ne l'écrasera pas.
        if User.objects.filter(phone=phone).exists():
            self.stdout.write(f"L'admin {phone} existe déjà, rien à faire.")
            return

        try:
            validate_password(password)
        except ValidationError as e:
            self.stdout.write(self.style.WARNING(
                "Attention, mot de passe admin faible : " + " ".join(e.messages)
            ))

        User.objects.create_superuser(phone=phone, first_name=name, password=password)
        self.stdout.write(self.style.SUCCESS(f"Admin {name} ({phone}) créé."))
