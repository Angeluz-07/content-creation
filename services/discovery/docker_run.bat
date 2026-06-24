docker run -v "%cd%:/app/" --env-file=.env -p 8004:8004 --add-host=localhost:host-gateway -it angeluz07/cc-discovery:0.0.1 
