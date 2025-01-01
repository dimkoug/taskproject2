=====
Django taskproject application
=====

Quick start
-----------

1. Clone repo  like this::

      git clone  https://github.com/dimkoug/taskproject2.git

2. Create a virtualenv::

    python3 -m venv venv

3. Activate virtualenv

4. Install packages from requirements.txt file


5. Create settings_local.py with settings from settings_local_sample.py

6. Run `python manage.py makemigrations users profiles companies invitations projects`

7. Run `python manage.py migrate`

8. Start the development server and visit http://127.0.0.1:8000/


=====
Todo
=====

1. Remove class based  views and develop the frontend with a frontend framework with django rest
