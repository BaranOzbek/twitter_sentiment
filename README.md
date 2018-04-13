## Mood Barometer
This application will stream twitter and displayed sentiment values.

Using WebSockets to create a persistent connection to clients, the Server can
 broadcast real time updates.

 To run simply:
>  `pip install -r requirements.txt`
>  `python -m textblob.download_corpora`
>  `python server.py`

Note: Need to add consumer keys and secrets to authorise a connection with Twitter.
