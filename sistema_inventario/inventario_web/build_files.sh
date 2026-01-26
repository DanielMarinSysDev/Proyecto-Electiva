# build_files.sh
echo "Building the project..."
python3.9 -m pip install -r requirements.txt
python3.9 manage.py collectstatic --noinput --clear
# Asegurar que las migraciones se ejecuten
echo "Running migrations..."
python3.9 manage.py makemigrations
python3.9 manage.py migrate --noinput
echo "Migrations finished."

# Crear superusuario
python3.9 create_superuser.py
echo "Build complete."
