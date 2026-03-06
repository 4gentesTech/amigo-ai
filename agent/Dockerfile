FROM python:3.11-slim

WORKDIR /app

# Instala Poetry
RUN pip install poetry==1.7.1

# Copia arquivos de dependências
COPY pyproject.toml ./

# Instala dependências (sem dev)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copia código fonte
COPY src/ ./src/

# Expõe porta
EXPOSE 8000

# Comando de inicialização
CMD ["python", "-m", "src.main"]
