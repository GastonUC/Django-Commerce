#Base Image / Buiild stage
FROM python:3.10-slim AS builder

# Working directory
WORKDIR /app

# Install any needed packages specified in requirements.txt
# Install dependencies, --user flag is used to install packages in the user directory, on this case /root/.local
# --no-cache-dir flag is used to avoid caching the package index
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

#Final stage
FROM python:3.10-slim

WORKDIR /app

# Copy only the dependencies installation from the 1st stage image
COPY --from=builder /root/.local /root/.local
COPY . .

# Ensure the installed packages are in the PATH
ENV PATH=/root/.local/bin:$PATH

# Expose port that runs the app
EXPOSE 8000

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]