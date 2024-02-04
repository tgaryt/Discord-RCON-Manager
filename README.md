# Discord RCON Manager

## Introduction
This Discord bot was created by [tgaryt](https://ugc-gaming.net/index.php?members/ryt.3/) for [UGC-Gaming.NET](https://ugc-gaming.net) and is designed specifically for managing Source game servers.

## Commands

### RCON Command
- **Command**: `!rcon [server_group] [command]`
  - Sends an RCON command to a specified server group.
  - Example-1: `!rcon all sm_reloadadmins
  - Example-2: `!rcon all sv_password "rytpro"`

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
This project is licensed under the [MIT License](LICENSE.txt).
