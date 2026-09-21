#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend_django/requirements.txt

echo "==> Running Django database migrations..."
python backend_django/manage.py migrate --no-input

echo "==> Seeding database with realistic mutual fund analytics data..."
python backend_django/manage.py seed_data

echo "==> Training Scikit-Learn ML Churn model..."
python backend_django/manage.py train_churn_model

echo "==> Collecting static assets for WhiteNoise..."
python backend_django/manage.py collectstatic --no-input

echo "==> Build complete successfully!"
