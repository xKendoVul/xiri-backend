"""
Command para crear usuarios de prueba.

Uso:
    python manage.py create_test_users

Crea:
- 1 admin (admin/admin123)
- 3 usuarios normales (user1/user123, user2/user123, user3/user123)
- 2 owners (owner1/owner123, owner2/owner123)
"""
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Crear usuarios de prueba para desarrollo'

    def handle(self, *args, **options):
        # Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@xiri.com',
                'first_name': 'Admin',
                'last_name': 'Xiri',
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('  - Admin creado: admin / admin123'))
        else:
            self.stdout.write(f'  - Admin ya existía: admin')

        # Usuarios normales
        for i in range(1, 4):
            user, created = User.objects.get_or_create(
                username=f'user{i}',
                defaults={
                    'email': f'user{i}@xiri.com',
                    'first_name': f'Usuario',
                    'last_name': f'{i}',
                    'rol': 'user',
                }
            )
            if created:
                user.set_password('user123')
                user.save()
                self.stdout.write(f'  - Usuario creado: user{i} / user123')
            else:
                self.stdout.write(f'  - Usuario ya existía: user{i}')

        # Owners
        for i in range(1, 3):
            owner, created = User.objects.get_or_create(
                username=f'owner{i}',
                defaults={
                    'email': f'owner{i}@xiri.com',
                    'first_name': f'Owner',
                    'last_name': f'{i}',
                    'rol': 'owner',
                }
            )
            if created:
                owner.set_password('owner123')
                owner.save()
                self.stdout.write(f'  - Owner creado: owner{i} / owner123')
            else:
                self.stdout.write(f'  - Owner ya existía: owner{i}')

        self.stdout.write(self.style.SUCCESS('\n¡Usuarios de prueba creados exitosamente!'))
        self.stdout.write('\nCredenciales:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Usuarios: user1, user2, user3 / user123')
        self.stdout.write('  Owners: owner1, owner2 / owner123')
