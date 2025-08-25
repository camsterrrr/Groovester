# 🎵🎧 Groovester 🎧🎵

Want a groovy Discord voice channel? 😉 Groovester is a Discord bot that can build up a queue of song requests, join Discord voice channels, and play requested songs for all to enjoy! 😁

## Quick-Glance Commands

```
!help, used to display useful commands.

!join, used to join the voice channel the message author is connected to.
!leave, used to disconnect from the voice channel Groovester is connected to.

!play *url to YouTube video*, used to download a YouTube video to the local file system and queue it for playing in the voice channel.
!queue, used to print the queue of songs.
!stop, used to halt Groovester's "speaking" in the voice channel.
```

## How to Host Groovester Yourself

Groovester was developed using a Virtual Box virtual machine running Ubuntu 22.04 LTS. Python is cross-platform programming language, so installing packages with `pip` shouldn't be an issue. If you have a different operating system, or flavor of Linux, only the package manager commands should be different. 😉

If you have an issue running this application on a specific operating system, consider submitting a pull request with your own instructions. 😁

### Step 1️⃣: Package Setup

This Discord bot relies on Python 3 and several Python modules in order to operate. 

Assuming you're using Linux Ubuntu, you can install Python 3 using the package manager as listed below. 
- If you're operating system is not a flavor of Ubuntu, you will need to look up the command for your specific Linux distribution. 
- If you're on Windows or macOS you'll need to find a Python installer. This process can be tedious for beginners, please defer to a YouTube video for an installation guide.

```bash
apt install -y python3 ffmpeg
```

You can install all of the Python modules via the Python package manager.

```bash
pip install --upgrade Discord.py pytube python-dotenv validators pynacl ffmpeg
```

### ♟️ Step 1: Cloning

Clone this repository.

```bash
git clone https://github.com/camsterrrr/Groovester.git
```

### Step 2️⃣: Setting Up the Environment ⚙️

You'll need to create your own Discord application and get your own Discord bot token. I won't go into detail here isnce there are plenty of guides, though I'll provide a relevant resource below.

Todo: link

Additionally, you'll need to enable Developer mode in your Discord client in order to copy your Discord server's guild ID. Again, not going into detail, but I'll provide a relevant resource below.

Todo: link

Before you read any further, ensure that after you've created a Discord application and have added it to the server of your choice.

Open this application's directory on your local machine and create a file named `.env`. If you locate it anywhere besides the top-level directory, then you will need to modify the source code to read the `.env` file from that location. When creating your .env file, format it as follows:

```
Groovester/.env
    bot_token = "your token wrapped in quotes"
    guild_id = "your guild ID wrapped in quotes"
```

### Step 3️⃣: Running the Application (via shell terminal) 🏃‍♂️

Open a terminal and navigate to this applications directory on your local file system.

If you were to run the application it will take the foreground of the terminal, which means you can't do anything in the terminal until the process ends or is killed. To have the application run in the background, we can use the `screen` command, which allows us to create a session and reattach and detach to the session, sort of like switching between the different tabs in a web browser. Plus, `screen` sessions keep context and history past the lifetime of the terminal's session, so if your SSH connection or terminal ends, the screen `session` will still be re-attachable. 

To create a new `screen` instance run the following command.

```bash
screen -dmS Groovester
screen -S Groovester -X stuff "^M"
screen -S Groovester -X stuff "python3 -m src.main^M"
```

To re-attach into the `screen` session, issue the following command.

```bash
screen -rS Groovester
```

To detach from the `screen` session, press `ctrl + d`. The application will still be running in the background and any log messages printed will be displayed when you "tab" back into the session.

If you need to delete the `screen` sessions, you can do so safely by issuing the following commands. 

```bash
screen -ls
	There are screens on:
	        18895.Groovester        (07/08/2024 06:06:54 PM)        (Detached)
	        18869.Groovester        (07/08/2024 06:04:24 PM)        (Attached)
screen -XS 18895.Groovester quit
```

### Step 4️⃣: Issuing a Command (via Discord) ♟️

If you closely followed the steps listed up to this point, you should be okay to start issuing commands for Groovester. 

Let's start with `!help`. From the Discord client, navigate to the sever that you added the Discord application to (Step 2). Once there, go into any text channel and type "!help". 

Groovester should reply with the following message: 

```
!play usage:     !play URL to YouTube URL
    Groovester will download YouTube video and play it in a voice channel!

    ...
```

### Step 5️⃣: Troubleshooting 📝

Groovester's source code defines log messages will be stored in the `Groovester.log` file located within the Groovester directory. Any debug, info, and error messages will be written there. This application has exception handling where needed, so any error messages should be properly handled and logged.

Alternatively, you can view log messages that are created by Discord.py by reattaching to the screen session. Any log output in the terminal (not Groovester.log) comes from the Discord.py API. See instructions listed in Step 3️⃣ to reattach to the screen session.

## Contributors 🫂

camsterrrr (Oakley.CameronJ@gmail.com)

Special thanks to all of the online resources (Discord.py API Docs, StackOverflow, Reddit, No Starch Press books) I used while developing this. 🙂 There are too many to list, I extend my appreciation either way. 🙌
