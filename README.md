#To run the application follow the steps.

# 1. Install Python dependencies
1. Go to the app directory (SF_Project).
2. pip install -r requirements.txt

# 2. Link to the database, run migrations
1. Go to the app directory (SF_Project).
2. run: python manage.py makemigrations
3. run: python manage.py migrate


# 3. Run Django dev server
1. Go to the app directory (SF_Project).
2. run: python manage.py runserver