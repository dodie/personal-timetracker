Remove-Item venv -r -fo
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt