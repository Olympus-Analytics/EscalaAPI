# Pon este comando en la consola primero docker build -t django-gdal-app .
# Luego
# chmod +x init.sh en la consola
# por ultimo pon esto ./init.sh
docker run -p 8000:8000 -v $(pwd):/app django-gdal-app
