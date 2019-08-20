from django.apps import AppConfig


class RepoConfig(AppConfig):
    name = 'apps.repo'

    def ready(self):
        from .single import handler