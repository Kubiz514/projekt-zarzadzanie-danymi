Po pobraniu repozytorium aplikacji, należy
Pobrać Pythona w wersji 3.12.
Utworzyć wirtualne środowisko, np.
	$ python -m venv venv
	$ venv\Scripts\activate
Pobrać dependencje:
$ pip install -r requirements.txt
Utworzyć plik \app\secrets.yaml
Uzupełnić plik o secret key:
$ SECRET_KEY: my_secret_key_goes_here
Uruchomić aplikację:
$ uvicorn main:app --reload
Po uruchomieniu, w przeglądarce pod adersem http://127.0.0.1:8000/docs pojawi się UI dokumentacji API w postaci narzędzia Swagger.
