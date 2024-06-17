from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Executa migrações e cria um superusuário com username "admin" e senha "123".'

    def handle(self, *args, **kwargs):
        # Executa as migrações
        call_command('migrate')

        # Verifica se o superusuário 'admin' já existe
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.NOTICE('O superusuário "admin" já existe. Pulando a criação.'))
        else:
            # Cria o superusuário 'admin' com senha '123'
            try:
                User.objects.create_superuser('admin', 'admin@example.com', '123')
                self.stdout.write(self.style.SUCCESS('Superusuário "admin" criado com sucesso!'))
            except Exception as e:
                raise CommandError(f'Erro ao criar superusuário: {str(e)}')
        self.stdout.write(self.style.SUCCESS('Aplicativo instalado com sucesso!'))
