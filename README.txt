DIFFERENCE BETWEEN server/server.py AND server/server2.py:
    first is a simple variant, one-time and only for two players. After game finishing, server will shut down.
    Not supporting.

    second is more powerful variant. It has got rooms (for as much users as you want), timeout for clients,
    config, more settings, better output, more sustained to errors. Currently in developing.
    Supporting.

HOW TO USE THE CLIENT:
    just run python3 game.py for running on localhost (made for testing). For connecting to the online servers,
    run python3 game.py ip:port

HOW TO USE THE SERVER:
    to run server/server.py, just run python3 server/server.py

    to run server/server2.py, just run python3 server/server2.py. To load settings from config file (server-conf.json
    as default, you can change file in the source), run it with an argument --use-config