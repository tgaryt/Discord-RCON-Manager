# Discord RCON Manager

## Introduction
This Discord bot was created by [tgaryt](https://ugc-gaming.net/index.php?members/ryt.3/) for [UGC-Gaming.NET](https://ugc-gaming.net) and is designed specifically for managing Source game servers.

## Requirements

- **Python:** Version 3.7.3
- **discord.py:** Version 1.7.3
- **python-valve:** Version 0.2.1
- **Discord Bot Configuration:** Ensure that the bot has all Privileged Gateway Intents enabled.

## Installation

```bash
# Update package lists
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip

# Navigate to the project directory
cd your-bot-directory

# Install Python virtual environment
sudo apt install python3-venv

# Create a virtual environment
python3 -m venv rcon

# Activate the virtual environment
source rcon/bin/activate

# Install the required Python libraries
pip install discord.py
pip install python-valve

# Run the bot in the background using nohup
nohup python rcon-manager.py &

# Deactivate the virtual environment
deactivate
```
## Commands

### RCON Command
- **Command**: `!rcon [server_group] [command]`
  - Sends an RCON command to a specified server group.
  - Example-1: `!rcon all sm_reloadadmins
  - Example-2: `!rcon all sv_password "tgaryt"`

### Server Management
- **Add Server**: `!add_sv [server_group] [ip] [port]`
  - Adds a server to the specified server group.
  - Example: `!add_sv all 127.0.0.1 27015`

- **Remove Server**: `!rm_sv [server_group] [ip] [port]`
  - Removes a server from the specified server group.
  - Example: `!rm_sv all 127.0.0.1 27015`

### Command Management
To add or remove commands, use the `!add_cmd` and `!rm_cmd` commands. Ensure the specified file is included in `AutoFilePaths`.

- **Add Command**: `!add_cmd [auto_file_name] [command_name] [command_value]`
  - Adds a command to the specified file. Commands in the file will be automatically executed at regular intervals, as configured in the `config.ini` file. The commands will be sent to all servers listed in the file.
  - Example-1: `!add_cmd auto2fort sm_reloadadmins
  - Example-2: `!add_cmd auto2fort sv_password "rytpro"`

- **Remove Command**: `!rm_cmd [file_name] [command_name]`
  - Removes a command from the specified file.
  - Example: `!rm_cmd auto2fort sm_who`

## Configuration

### Auto-Generated Files
The bot automatically generates configuration files based on the specified `AutoFilePaths` in the `config.ini` file.

### Reloading Configuration
The bot automatically reloads its configuration every minute. There is no need to restart the bot unless the token is changed.

## License
This project is licensed under the [MIT License](LICENSE).
