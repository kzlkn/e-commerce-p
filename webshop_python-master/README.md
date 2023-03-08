# Best practices and guidelines

# DO NOT COMMIT db.sqlite3

#### Before working on this project, the following steps should be done: 
1. Activate your virtual environment : `venv\Scripts\activate` (for windows)
2. Update your local project: `git pull`
3. Install required modules: `pip3 install -r requirements.txt`


#### Before commiting and pushing any changes to the shared, remote repository: 
1. Make sure the project is executable: ` python .\manage.py runserver` (for windows)
2. Update all required modules for the project: `pip3 freeze > requirements.txt` 


#### Troubleshooting: 
Sometimes, migration files can cause a conflict if the collection is not chronologically consistent (e.g. migrations 1,2,3,6,9 - files 4,5,7,8 are missing)

You can solve this error by simply deleting all migrations files located under `./migrations` EXCEPT FOR any `__init__.py` file.
