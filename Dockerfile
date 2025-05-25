# Use Python slim image as base
FROM python:3.9-slim

# Add labels for better maintainability
LABEL description="Labeler for pairs of descriptions"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOME=/home/appuser \
    APP_HOME=/home/appuser/app

# Create a non-privileged user
RUN groupadd -r appuser && useradd -r -g appuser -d ${HOME} -s /sbin/nologin -c "validator user" appuser

# Set up the working directory
WORKDIR ${APP_HOME}

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
# COPY example_data.csv .

# Create directory for output files and set permissions
RUN mkdir -p ${APP_HOME}/output && \
    chown -R appuser:appuser ${HOME}

# Switch to non-privileged user
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Set up Streamlit configuration
RUN mkdir -p ${HOME}/.streamlit
COPY config.toml ${HOME}/.streamlit/config.toml

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"] 