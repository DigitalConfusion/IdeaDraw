pip install -r requirements.txt
cd app
flask --app __init__:create_app() run --reload
pause