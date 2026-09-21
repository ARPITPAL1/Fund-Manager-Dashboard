from django.core.management.base import BaseCommand
from analytics_api.ml.train_churn_model import train_and_save_model

class Command(BaseCommand):
    help = 'Train and export the Scikit-Learn Random Forest Churn Classifier model'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting Churn Model training pipeline...'))
        train_and_save_model()
        self.stdout.write(self.style.SUCCESS('Churn model trained and saved successfully!'))

