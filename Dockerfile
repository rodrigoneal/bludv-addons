docker run -d \
    -p 8000:27017 \
    --name test-mongo \
    -v data-vol:/data/db \
    mongo:latest