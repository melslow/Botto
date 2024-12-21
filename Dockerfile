# Use the official lightweight Python image.
FROM python:3.10-slim

# Create a directory for your application.
WORKDIR /app

# Copy only the requirements first to leverage Docker layer caching.
COPY requirements.txt ./

# Install the required Python packages.
RUN pip install --no-cache-dir -r requirements.txt

# Get FFMPEG
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Now copy the rest of the Botto code into the container.
COPY . .

# Use "python botto.py" as the default command.
# If your main file or start script is named differently, adjust the command.
CMD ["python", "bot.py"]
