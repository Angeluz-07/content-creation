docker run -v "%cd%:/app/" -p 8000:8000 --env-file=.env --add-host=localhost:host-gateway -it angeluz07/cc-production:0.0.1 
