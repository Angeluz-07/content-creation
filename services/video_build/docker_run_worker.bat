docker run -v "%cd%:/app/" --env-file=.env --add-host=localhost:host-gateway -it angeluz07/cc-video-build:0.0.1 ^
    taskiq worker workers.broker:broker workers.video_build ^
    --workers 2
