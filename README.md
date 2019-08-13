# API Challenge #

To install this project using Pipenv run:

`pipenv install`

If you run it using pipenv you'll need to run `pipenv shell` before the other commands.

After that migrate the database through these commands:
```
python -m flask db migrate
python -m flask db upgrade
```

To run the project:

`python -m flask run`

To run tests just run:

`python tests.py`

To POST to Prescriptions API (http://localhost:5000/v2/prescriptions/) you should send a request with the following data:

```
{
  "clinic": {
    "id": 1
  },
  "physician": {
    "id": 1
  },
  "patient": {
    "id": 1
  },
  "text": "Dipirona 1x ao dia"
}
```

On Windows you'll have to use cURL like so:

` curl  -H "Content-Type:application/json" -d "{\"clinic\":{\"id\":1},\"physician\":{\"id\":1},\"patient\":{\"id\":1},\"text\":\"Dipirona 1x ao dia\"}" -X POST http://localhost:5000/v2/prescriptions `

On Linux you might be able to use cURL like so:
```curl -X POST \
  http://localhost:5000/v2/prescriptions \  
  -H 'Content-Type: application/json' \
  -d '{
    "clinic": {
        "id": 1
    },
    "physician": {
        "id": 1
    },
    "patient": {
        "id": 1
    },
    "text": "Dipirona 1x ao dia"
}'
```

