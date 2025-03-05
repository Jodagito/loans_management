# Installation Steps

**Install Poetry**
```pip install poetry```

**Install dependencies**
This command should be ran inside the project folder where the pyproject.toml is located
```poetry install```

**Activate Poetry env**
```poetry env activate```
This will print the activate command of the virtual environment to the console, then you can run the output command manually. [Poetry related docs.]([/guides/content/editing-an-existing-page](https://python-poetry.org/docs/managing-environments/#activating-the-environment))

**Create the database**
This command should be ran within the folder where the migrate.py file is located
```python manage.py migrate```

**Run the server**
```python manager.py runserver```
This will run the server in localhost and will only be accessible by your machine

**Run the server for any machine in your network**
```python manager.py runserver 0.0.0.0```
This will run the server in localhost and will be accesible for any device in your network by using your local ip address
