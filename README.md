** windows
python -m venv .venv
.venv\Scripts\activate.bat
#if it fails -> Set-ExecutionPolicy Unrestricted -Scope Process
python

** python common
* save pip history
pip freeze > requirements.txt
* load pip history
pip install -r requirements.txt
