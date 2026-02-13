# Usamos una imagen base ligera de Python
FROM python:3.9-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias
# build-essential y curl para healthcheck
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero el archivo de requerimientos para aprovechar la caché de Docker
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la aplicación
COPY . .

# Exponemos el puerto por defecto de Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Healthcheck básico
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1
