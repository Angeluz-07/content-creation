docker run -v "%cd%:/app/" -p 8002:8002 --env-file=.env --add-host=localhost:host-gateway -it angeluz07/cc-download:0.0.1 
