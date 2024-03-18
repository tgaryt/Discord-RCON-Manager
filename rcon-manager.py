import discord
from discord.ext import commands, tasks
from discord import Embed
import valve.rcon
import logging
from datetime import datetime
import os
import asyncio
import configparser
import mysql.connector
import aiohttp

intents = discord.Intents.default()
intents.all()
intents.message_content = True
intents.presences = True
intents.members = True

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['Bot']['Token']
RCON_PASSWORD = config['Bot']['RconPassword']
LOOP_INTERVAL = int(config['Bot']['LoopInterval'])
AUTO_FILE_PATHS = [os.path.join('groups', file_name.strip()) for file_name in config['Bot']['AutoFilePaths'].split(',')]

bot = commands.Bot(command_prefix='!', intents=intents)

def create_auto_files():
    for file_path in AUTO_FILE_PATHS:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write('[servers]\n\n')
                file.write('[commands]\n')

        all_file_path = os.path.join('groups', 'all.txt')
    if not os.path.exists(all_file_path):
        os.makedirs(os.path.dirname(all_file_path), exist_ok=True)
        with open(all_file_path, 'w') as file:
            file.write('[servers]\n')

    log_file_path = 'rcon.log'
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w'):
            pass

def read_servers_from_file(file_path):
    with open(file_path, 'r') as file:
        servers = [line.strip().split() for line in file.readlines()]
    return servers

def read_servers_and_commands_from_file(file_path):
    servers = []
    commands = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('[servers]'):
                servers_section = True
                commands_section = False
                continue
            elif line.startswith('[commands]'):
                servers_section = False
                commands_section = True
                continue

            if servers_section:
                server_info = line.split()
                if len(server_info) == 2:
                    ip, port = server_info
                    servers.append((ip, port))
            elif commands_section:
                commands.append(line)

    return servers, commands

def read_servers_from_file(file_path):
    servers = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

        in_servers_section = False

        for line in lines:
            line = line.strip()

            if line.startswith('['):
                in_servers_section = False

            if in_servers_section and line:
                server_info = line.split()
                if len(server_info) == 2:
                    ip, port = server_info
                    servers.append((ip, port))

            if line.lower() == '[servers]':
                in_servers_section = True

    return servers

def log_command_used(username, command):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{current_time} - {username} - {command}\n"
    log_file_path = 'rcon.log'

    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as new_log_file:
            pass

    with open(log_file_path, 'a') as log_file:
        log_file.write(log_message)

@tasks.loop(seconds=LOOP_INTERVAL)
async def automatic_rcon():
    for file_path in AUTO_FILE_PATHS:
        servers, commands = read_servers_and_commands_from_file(file_path)

        for ip, port in servers:
            try:
                with valve.rcon.RCON((ip, int(port)), RCON_PASSWORD) as rcon:
                    for command in commands:
                        response = rcon.execute(command)
                        print(f"Command sent to {ip}:{port}: {command}")
            except valve.rcon.RCONError as e:
                print(f"Failed to send command to {ip}:{port}: {e}")
            except asyncio.CancelledError:
                print("Task cancelled. Closing RCON connections.")
                return

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if isinstance(message.channel, discord.DMChannel):
        return

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    automatic_rcon.start()
    create_auto_files()

@bot.command()
async def rcon(ctx, server_group, *, command):
    file_path = f'groups/{server_group}.txt'

    if not server_group or not command:
        await ctx.send("Usage: !rcon [server_group] [command]")
        return

    if not file_path:
        await ctx.send(f"No server information found for group {server_group}")
        return

    servers = read_servers_from_file(file_path)

    success_count = 0
    failure_count = 0
    failure_servers = []

    for ip, port in servers:
        try:
            with valve.rcon.RCON((ip, int(port)), RCON_PASSWORD) as rcon:
                response = rcon.execute(" ".join(command.split()))
            success_count += 1
        except valve.rcon.RCONError as e:
            failure_count += 1
            failure_servers.append((ip, port))
            print(f"Failed to connect to {ip}:{port} - {e}")
        except ConnectionRefusedError as e:
            print(f"Connection refused for {ip}:{port} - {e}")
        except Exception as e:
            print(f"An error occurred for {ip}:{port} - {e}")

    embed_summary = Embed(
        title=f'RCON Command Summary - {server_group}',
        color=discord.Color.blue()
    )

    summary_description = f'RCON command summary for `{command}`:\n\n'

    if success_count == len(servers):
        summary_description += 'Command sent successfully to all servers.\n\n'
    elif success_count > 0:
        summary_description += f'Command sent successfully to {success_count} server(s).\n\n'

    if failure_count > 0:
        failed_servers_str = '\n'.join([f'{ip}:{port}' for ip, port in failure_servers])
        summary_description += f'Command failed to be sent to {failure_count} server(s):\n{failed_servers_str}'

    embed_summary.description = summary_description

    await ctx.send(embed=embed_summary)
    log_command_used(ctx.author.name, command)

@bot.command()
async def add_sv(ctx, server_group, ip, port):
    file_path = f'groups/{server_group}.txt'

    if not server_group or not ip or not port:
        await ctx.send("Usage: !add_sv [server_group] [ip] [port]")
        return

    servers, commands = read_servers_and_commands_from_file(file_path)

    if (ip, port) in servers:
        await ctx.send(f'Server `{ip}:{port}` already exists in server group `{server_group}`')
    else:
        servers.append((ip, port))

        with open(file_path, 'r') as file:
            lines = file.readlines()

        servers_index = 0
        for i, line in enumerate(lines):
            if line.startswith('[servers]'):
                servers_index = i
                break
            elif line.startswith('['):
                servers_index = i
                lines.insert(i, '[servers]\n')
                break

        lines.insert(servers_index + 1, f'{ip} {port}\n')

        with open(file_path, 'w') as file:
            file.writelines(lines)

        await ctx.send(f'Server `{ip}:{port}` added to server group `{server_group}`')

@bot.command()
async def rm_sv(ctx, server_group, ip, port):
    file_path = f'groups/{server_group}.txt'

    if not server_group or not ip or not port:
        await ctx.send("Usage: !rm_sv [server_group] [ip] [port]")
        return

    servers, commands = read_servers_and_commands_from_file(file_path)

    if (ip, port) in servers:
        servers.remove((ip, port))

        with open(file_path, 'r') as file:
            lines = file.readlines()

        servers_start_index = 0
        servers_end_index = len(lines)
        for i, line in enumerate(lines):
            if line.startswith('[servers]'):
                servers_start_index = i + 1
            elif line.startswith('['):
                if servers_start_index != 0:
                    servers_end_index = i
                    break

        updated_lines = lines[:servers_start_index] + [f'{ip} {port}\n' for ip, port in servers] + lines[servers_end_index:]
        
        with open(file_path, 'w') as file:
            file.writelines(updated_lines)

        await ctx.send(f'Server `{ip}:{port}` removed from server group `{server_group}`')
    else:
        await ctx.send(f'Server `{ip}:{port}` does not exist in server group `{server_group}`')

@bot.command()
async def add_cmd(ctx, file_name, command_name, *command_value):
    file_path = f'groups/{file_name}.txt'

    if os.path.basename(file_path) not in [os.path.basename(path) for path in AUTO_FILE_PATHS]:
        await ctx.send(f"Command modification is only allowed for files in {', '.join(AUTO_FILE_PATHS)}")
        return

    if not file_name or not command_name:
        await ctx.send("Usage: !add_cmd [file_name] [command_name] [command_value]")
        return

    servers, commands = read_servers_and_commands_from_file(file_path)

    commands = [cmd for cmd in commands if not cmd.startswith(command_name)]

    if command_value:
        full_command = f'{command_name} "{command_value[0]}"'
    else:
        full_command = command_name

    if full_command in commands:
        await ctx.send(f'Command `{full_command}` already exists in the configuration file `{file_name}.txt`.')
    else:
        commands.append(full_command)
        with open(file_path, 'w') as file:
            file.write('[servers]\n')
            for server in servers:
                file.write(f'{server[0]} {server[1]}\n')
            file.write('\n[commands]\n')
            for updated_command in commands:
                file.write(f'{updated_command}\n')
        await ctx.send(f'Command `{full_command}` added to the configuration file `{file_name}.txt`.')

@bot.command()
async def rm_cmd(ctx, file_name, command_name):
    file_path = f'groups/{file_name}.txt'

    if os.path.basename(file_path) not in [os.path.basename(path) for path in AUTO_FILE_PATHS]:
        await ctx.send(f"Command modification is only allowed for files in {', '.join(AUTO_FILE_PATHS)}")
        return

    if not file_name or not command_name:
        await ctx.send("Usage: !rm_cmd [file_name] [command_name]")
        return

    servers, commands = read_servers_and_commands_from_file(file_path)

    commands = [cmd for cmd in commands if not cmd.startswith(command_name)]

    with open(file_path, 'w') as file:
        file.write('[servers]\n')
        for server in servers:
            file.write(f'{server[0]} {server[1]}\n')
        file.write('\n[commands]\n')
        for updated_command in commands:
            file.write(f'{updated_command}\n')

    await ctx.send(f'Command `{command_name}` removed from the configuration file `{file_name}.txt`.')

@bot.command(name='rcon-command')
async def rcon_command(ctx, *, command):
    db_connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    cursor = db_connection.cursor()

    cursor.execute(f'SELECT ip, port FROM {DB_TABLE}')
    servers = cursor.fetchall()

    command_responses = {}

    async with aiohttp.ClientSession() as session:
        for ip, port in servers:
            try:
                with valve.rcon.RCON((ip, port), RCON_PASSWORD) as rcon:
                    response = rcon.execute(command)
                command_responses[(ip, port)] = response.text
            except Exception as e:
                command_responses[(ip, port)] = f"Error: {str(e)}"

    cursor.close()
    db_connection.close()

    extracted_responses = {}
    for ip_port, response in command_responses.items():
        extracted_response = {}
        for line in response.split("\n"):
            if "=" in line:
                key_value_pair = line.strip().split("=", 1)
                if len(key_value_pair) == 2:
                    key, value = key_value_pair
                    key = key.strip().strip('"')
                    value = value.strip().strip('"')
                    extracted_response[key] = value
        extracted_responses[ip_port] = extracted_response

    response_counts = {}
    for response in extracted_responses.values():
        response_str = '|'.join([f"{k}={v}" for k, v in response.items()])
        response_counts[response_str] = response_counts.get(response_str, 0) + 1

    most_common_response = max(response_counts, key=response_counts.get)

    different_responses = {}
    for ip_port, response in extracted_responses.items():
        response_str = '|'.join([f"{k}={v}" for k, v in response.items()])
        if response_str != most_common_response:
            different_responses[ip_port] = response

    if len(different_responses) == 0:
        response_str = f'All servers have "{command}" set to {most_common_response}.'
    else:
        response_str = f'Most servers have "{command}" set to {most_common_response}, except for:\n'
        for ip_port, response in different_responses.items():
            response_str += f"- {ip_port[0]}:{ip_port[1]} ({', '.join([f'{key}={value}' for key, value in response.items()])})\n"

    await ctx.send(response_str)

bot.run(TOKEN)
