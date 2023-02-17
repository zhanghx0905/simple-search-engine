```
# Set up environment
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# run backend server
# flask run
waitress-serve --listen=127.0.0.1:5000 app:APP
```

