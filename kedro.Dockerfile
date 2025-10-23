FROM job-finder-base:latest

WORKDIR /app

# Copy requirements Kedro
COPY kedro_requirements.txt /app/kedro_requirements.txt

# Installer les dépendances Kedro supplémentaires
RUN python -m pip install --no-cache-dir -r kedro_requirements.txt

# Copy pyproject.toml et README.md (requis par hatchling)
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md

# Copy project files
COPY src/ /app/src/
COPY conf/ /app/conf/

# Installer le package en mode éditable (sans dépendances pour éviter les conflits)
RUN pip install -e . --no-deps

EXPOSE 8888
CMD ["kedro", "run"]
