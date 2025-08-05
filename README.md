# Groovester

Want a groovy Discord voice channel? Groovester is a Discord Application that can build up a queue of song requests, join Discord voice channels, and play requested songs for all to enjoy!

## Groovester's Commands

```
!help, used to display useful commands.

!join, used to join the voice channel the message author is connected to.
!leave, used to disconnect from the voice channel Groovester is connected to.

!play *url to YouTube video*, used to download a YouTube video to the local file system and queue it for playing in the voice channel.
!queue, used to print the queue of songs.
!stop, used to halt Groovester's "speaking" in the voice channel.
```

## Tree

```
Groovester
|———————— .env
|———————— .git
|———————— src
|          |———————— __init__.py   ; Empty file that makes "src" act as a Python module.
|          |———————— _logging_.py  ; Used to sync logging settings among all files.
|          |———————— client.py     ; Catches and responds to all client events.
|          |———————— constants.py  ; Defines all of the messages that are logged or sent as a message.
|          |———————— Groovester.py ; Contains all of the main application logic.
|———————— test
|————————README.md
```

## How to Host Groovester Yourself

### Option 1: Docker (Recommended)

The easiest way to run Groovester is using Docker. This method works on Windows, macOS, and Linux.

#### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

#### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/camsterrrr/Groovester.git
   cd Groovester
   ```

2. **Set up your Discord bot token**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your Discord bot token
   # botToken="your_actual_discord_bot_token_here"
   ```

3. **Build and run with Docker Compose**
   ```bash
   # Build and start the container
   docker-compose up -d
   
   # View logs
   docker-compose logs -f groovester
   
   # Stop the container
   docker-compose down
   ```

#### Manual Docker Commands

If you prefer to use Docker directly:

```bash
# Build the image
docker build -t groovester .

# Run the container
docker run -d --name groovester-bot \
  -e botToken="your_discord_bot_token_here" \
  -v $(pwd)/downloads:/app/tmp/downloads \
  -v $(pwd)/logs:/app/logs \
  groovester

# View logs
docker logs -f groovester-bot

# Stop and remove the container
docker stop groovester-bot
docker rm groovester-bot
```

### Option 2: Manual Installation (Linux)

Groovester was developed using a Virtual Box virtual machine running Ubuntu 22.04 LTS. If you have a different operating system, or flavor of Linux, only the package manager commands should be different.

If you're on Windows, we recommend using the Docker method above.

### Step 0: Package Setup

This Discord Application relies on Python 3 and several Python modules in order to operate. 

Assuming you're using Linux Ubuntu, you can install Python 3 using the package manager as listed below. 
- If you're operating system is not a flavor of Ubuntu, you will need to look up the command for your specific Linux distribution. 
- If you're on Windows you'll need to find a Python installer. This process can be tedious for beginners, please defer to a YouTube video for an installation guide.

```bash
apt install python3
```

You can install all of the Python modules via the Python package manager using the requirements.txt file:

```bash
# Install all required Python packages
pip install -r requirements.txt
```

Alternatively, you can install them manually:

```bash
pip install --upgrade Discord.py pytube python-dotenv validators pynacl ffmpeg		
```

### Step 1: Cloning

Clone this repository.

```bash
git clone https://github.com/camsterrrr/Groovester.git
```

### Step 2: Setting Up the Environment

You'll need to create your own Discord application and get your own Discord Application token. There are plenty of guides out there for creating an Application, so I won't go into detail here... 

Before you read any further, ensure that after you've created a Discord application, you add it to your server of choice.

Currently, the Groovester application will pull the application token from a .env file, which is expected to be in the Groovester top-level directory on your local machine. If you locate it anywhere else, you may need to modify the source code. When creating your .env file, format it as follows: `botToken = "your token wrapped in quotes"`.

Reference the "Tree" section as needed.

### Step 3: Running the Application

Before you read any further, set your working directory as Groovester.

Running the application will take the foreground of the terminal, which means you can't do anything in the terminal until the process ends or is killed. To have the application run in the background, we can use the `screen` command, which allows us to create a session and reattach and detach to the session, sort of like switching between the different tabs in a web browser. Plus, `screen` sessions keep context and history past the lifetime of the terminal's session, so if your PuTTY or SSH connection ends, the screen `session` will still be re-attachable. 

To create a new `screen` instance run the following command.

```bash
screen -dmS Groovester
screen -S Groovester -X stuff "^M"
screen -S Groovester -X stuff "python3 -m src.client^M"
```

To "reattach" into the `screen` session, issue the following command.

```bash
screen -rS Groovester
```

To detach from the `screen` session, press `ctrl + d`. Don't worry, the application will still be running in the background and any log messages printed will be displayed when you "tab" back into the session.

If you somehow have messed up with the `screen` sessions, you can view and delete individual sessions with the following commands. 

```bash
screen -ls
	There are screens on:
	        18895.Groovester        (07/08/2024 06:06:54 PM)        (Detached)
	        18869.Groovester        (07/08/2024 06:04:24 PM)        (Attached)
screen -XS 18895.Groovester quit
```

### Step 4: Issuing a Command

If you closely followed the steps listed up to this point, you should be okay to start issuing commands for Groovester. 

Let's start with `!help`. From the Discord client, navigate to the sever that you added the Discord application to (Step 2). Once there, go into any text channel and type "!help". 

Groovester should reply with the following message: 

```
!play usage:     !play URL to YouTube URL
    Groovester will download YouTube video and play it in a voice channel!

    ...
```

### Step 5: Troubleshooting

Groovester's source code defines log messages will be stored in the `Groovester.log` file located within the Groovester directory. Any debug, info, and error messages will be written there. This application has exception handling where needed, so any error messages should be properly handled and logged.

Alternatively, you can view log messages that are created by Discord.py by reattaching to the screen session. Any log output in the terminal (not Groovester.log) comes from the Discord.py API. See instructions listed in Step 3 to reattach to the screen session.

### Step 6: Open-Source!

This is an open-source project after all! If you want to contribute a feature, or fork and create your own Discord application, feel free to!

## Details

### Logging

### Multi-Threaded Features

### Temporary Data

When issuing the `!play` command, Groovester will download the requested YouTube video and store it within `/tmp/Groovester/downloads`. Files within the `/tmp` directory are usually meant to be deleted. Groovester will delete files after it plays the song. However, if storage is an issue, take this directory into consideration.

## Notes

In this section, I'll list some seemingly random notes. This is more or less for my own recollection, in the event I ever need to revisit these issues.

- I had some issues with joining the bot to a voice channel. I had properly implemented the `!join` command and verified the application's permissions within my server, but the issues came down to my Ubuntu instance not having the PyNaCl package installed. After installing, the bot joined the voice channel without issues.
- I ran into some issues downloading YouTube audio using pytube. Every time I would try to invoke the "StreamObject" (YouTube.streams), it would throw the following exception (see below). The following PyTybe GitHub issue described a fix, which I followed to get pytube to successfully download YouTube audio. Link, https://github.com/pytube/pytube/issues/1954.

```
Traceback (most recent call last):
  . . .
pytube.exceptions.RegexMatchError: get_throttling_function_name: could not find match for multiple

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  . . .
pytube.exceptions.RegexMatchError: get_throttling_function_name: could not find match for multiple
```

## Contributors

camsterrrr (Oakley.CameronJ@gmail.com) (PGP)
mdnoyon9758 - Docker containerization, requirements.txt, and documentation improvements

Special thanks to all of the online resources I used while developing this :). There are too many to list, I extend my appreciation either way.
