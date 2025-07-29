This is a very basic project board I made for work.

#Install instructions

Works for both Windows and Linux\
database is created the first time you run app.py

Download the source code\
Make sure you have Python installed and in your PATH.

Edit options.csv to fit your needs. (changing the first row will break everything.)

# Linux terminal

from the root directory of the project.
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

# Windows terminal/powershell

from the root directory of the project.
```
venv\Scripts\Activate.ps1
# If you get an error that is can not be loaded because running scripts is disabled
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then try to run venv again.
pip install -r requirements.txt
python app.py
```

Then navigate to the address shown in your terminal from your browser.
