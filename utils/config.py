import os
import json
import secrets
from datetime import datetime

PREFIX = os.getenv("PREFIX", "-")


class Config:
    def __init__(self, client):
        self.client = client
        self.on_check = []

        self.commands_signs = [
            "Config",
            "Auto Role",
            "Audio",
            "Blocking",
            "Voice",
            "Test Management",
            "Homework Management",
            "Nick Change",
            "Roles",
            "Get Out",
            "Clear",
        ]

        self.file = ""
        self.config = ""
        self.servers = ""
        self.dm = ""
        self.settings = ""
        self.dm_settings = ""
        self.valid_users = ""
        self.blocked = ""
        self.blocked_server = ""

        self.category = {
            "name": "",
            "secret_code": "",
            "Tests": [],
            "Homeworks": [],
            "Prefix": PREFIX,
            "LogChannel": "",
            "DJ": "False",
            "Reactions": {},
            "check_list": {},
            "welcomeMsg": [],
            "forwarding": "",
        }
        self.categoryDM = {
            "name": "",
            "secret_code": "",
            "Tests": [],
            "Homeworks": [],
            "Prefix": PREFIX,
            "forwarding": "",
        }
        self.open_config()

    def open_config(self):
        self.file = open("utils/config.json", "r+")
        self.config = json.load(self.file)

        self.servers = self.config["servers"]
        self.dm = self.config["dm"]
        self.valid_users = self.config["valid_users"]
        self.blocked = self.config["blkd"]
        self.blocked_server = self.config["blkdSrv"]
        self.settings = self.config["settings_servers"]
        self.dm_settings = self.config["settings_dm"]

    def get_server(self, id, test="False"):
        self.open_config()

        try:
            if "DM" in str(id):
                spcificSrvr = self.dm.index(str(id))
                spcificSrvr = self.dm_settings[int(spcificSrvr)]
            else:
                spcificSrvr = self.servers.index(str(id))
                spcificSrvr = self.settings[int(spcificSrvr)]
        except:
            if "DM" in str(id):
                new_category = self.categoryDM

                self.dm.append(str(id))

                new_category["name"] = str(id)
                new_category["secret_code"] = self.gen_sc()
                self.dm_settings.append(new_category)
            else:
                new_category = self.category

                self.servers.append(str(id))

                new_category["name"] = str(id)
                new_category["secret_code"] = self.gen_sc()
                self.settings.append(new_category)

            self.save()

        if "DM" in str(id):
            spcificSrvr = self.dm.index(str(id))
            spcificSrvr = self.dm_settings[int(spcificSrvr)]
        else:
            spcificSrvr = self.servers.index(str(id))
            spcificSrvr = self.settings[int(spcificSrvr)]

        forw = str(spcificSrvr["forwarding"])

        if forw != "" and test == "False":
            spcificSrvr = self.servers.index(str(forw))
            spcificSrvr = self.settings[int(spcificSrvr)]

        return spcificSrvr

    def save(self):
        self.file.seek(0)

        json.dump(self.config, self.file, indent=1)

        self.file.truncate()
        self.file.close()

        self.open_config()

    def getID(self, ctx):
        try:
            id = str(ctx.guild.id)
        except:
            id = str(f"[DM] {ctx.author.id}")

        return id

    def getNAME(self, ctx, command):
        try:
            try:
                name = str(f"[{ctx.guild.id}] [{ctx.author.id}]:\> [{command}]")
            except:
                name = str(f"[{ctx.author}] [{ctx.author.id}]:\> [{command}]")
        except:
            try:
                name = str(f"[{ctx.guild.id}] [{ctx.id}]:\> [{command}]")
            except:
                name = str(f"[{ctx}] [{ctx.id}]:\> [{command}]")

        return name

    def gen_sc(self):
        return secrets.token_hex(8)

    async def get_time(self):
        now = datetime.utcnow()
        dt_string = now.strftime("%d/%m/%Y-%H:%M")
        return dt_string

    async def prnt(self, ctx, content, public=True):
        print(str(content).replace("\n", ""))

        if public:
            id = self.getID(ctx)

            log = self.get_server(str(id))
            new_id = log["name"]

            if "DM" not in new_id:
                log = log["LogChannel"]

                if str(log) != "":
                    for guild in self.client.guilds:
                        if str(guild.id) == str(new_id):
                            for channel in guild.channels:
                                if str(channel.id) == log:
                                    content = str(content).replace("`", "'")
                                    await channel.send(f"```{content}```")
                                    break
                            break

    async def blockCheck(self, ctx):
        self.open_config()

        try:
            blockedUsr = str(f"{ctx.guild.id}-{ctx.author.id}")
            blockedUsr2 = str(ctx.author.id)
        except:
            blockedUsr = "ProblemNONE"
            blockedUsr2 = "ProblemNONE"

        try:
            blockedSrv = str(ctx.guild.id)
        except:
            blockedSrv = "ProblemNONE"

        if (
            blockedUsr not in self.blocked
            and blockedSrv not in self.blocked_server
            and blockedUsr2 not in self.blocked
        ):
            return False
        else:
            return True

    async def on_checkk(self, ctx, comd, state):
        if not ctx.author.bot:
            id = self.getID(ctx)
            to_checkON = f"{id}|{comd}|{ctx.author.id}"

            if state and to_checkON not in self.on_check:
                self.on_check.append(to_checkON)
            elif not state and to_checkON in self.on_check:
                num_on = self.on_check.index(to_checkON)
                del self.on_check[num_on]
            else:
                return False

            return True
        else:
            return False


def get_prefix(client, message):
    config = Config(client)

    id = config.getID(message)
    prefix = config.get_server(str(id))
    prefix = prefix["Prefix"]

    return prefix
