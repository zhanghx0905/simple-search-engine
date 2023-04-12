# Set up environment
pip install -r requirements.txt
pip install ./lib/en_core_web_sm-3.5.0-py3-none-any.whl

# Run backend server
flask run # Debug server
# waitress-serve --listen=127.0.0.1:5000 app:APP