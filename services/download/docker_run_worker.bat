docker run -v "%cd%:/app/" --env-file=.env --add-host=localhost:host-gateway -it angeluz07/cc-download:0.0.1 ^
    taskiq worker workers.broker:broker workers.download ^
    --workers 2
