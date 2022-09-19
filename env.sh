echo "\n-------------------------------"
echo "Setting up Python Virtual ENV"
echo "-------------------------------\n"
python3 -m venv venv
source venv/bin/activate
echo "\n-------------------------------"
echo "Downloading dependencies..."
echo "-------------------------------\n"
pip install --upgrade pip
pip install -r requirements.txt
echo "\n-------------------------------"
echo "Start running Django server..."
echo "-------------------------------\n"
python manage.py runserver localhost:8000