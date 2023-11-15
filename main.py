from src.thingspeak import ThingSpeak
from src.utils import Utils
from src.canal import Channel
from src.field import Field

from colorama import Fore, init
import signal
import sys
import re

# u = Utils()
init()

# Method to handle the exit of the program when ctrl + c is pressed
def signal_handler(signum=None, frame=None):
    # ctrl + c
    if signum == signal.SIGINT:
        Utils.clear()
        sys.exit(0)
    # ctrl + l
    # elif signum == signal.SIGINFO:
    #     Utils.clear()
    else:
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGINFO, signal_handler)

# Method to check the user-api-token
def checkUserApyKey(user_api_key):
    Utils.clear()
    init()
    req = Utils.make_request(method="GET",
                            url=f"https://api.thingspeak.com/channels.json?api_key={user_api_key}")

    if req.status_code == 200:
        return True
    elif req.status_code == 401:
        return False


# Method to login
def login():
    while True:
        Utils.clear()
        str_banner = "1. Iniciar Sesion con CREDENCIALES.\n\n" \
                    "2. Iniciar sesion con APY KEY.\n\n" \
                    "CTRL + C para salir en cualquier momento.\n"

        option = Utils.endless_terminal(str_banner, "1", "2")
        Utils.clear()

        if option == "2":
            user_api_key = input("Introduce tu apy key: ")

            if checkUserApyKey(user_api_key):
                print(Fore.GREEN + "Successfull " + Fore.WHITE + "APY KEY provided.")
                Utils.wait_animation(1)
                # ts = ThingSpeak(user_api_key, u)
                # menu_principal(user_api_key)
            else:
                print(Fore.RED + "Wrong " + Fore.WHITE + "APY KEY provided.")
                Utils.wait_animation(1)
        i = input()


# Method to control de flow of a selected field
def field_menu(ts, channel, index, field_name):
    field = Field(index, field_name, channel.id, channel.write_api_key, channel.read_api_key)
    table = field.read_data_from_field()

    str_field_menu_help = "rename\trename the field\n" \
                        "upload\tupload data to the current field\n" \
                        "download data\tdownload data from the current field\n" \
                        "clear field\tclear all the data from this field\n" \
                        "delete field\tremove the field and all his data\n" \

    options_dict = {
        "upload": field.subir_datos,
        "download data": field.download_data,
        "clear field": field.clear_field_data,
        "delete field": field.delete_field
    }
    
    while True:
        option = Utils.endless_terminal(table, *list(options_dict.keys()), help_message=str_field_menu_help, menu=channel.channel_name, menu1=field_name, clear="yes")
    
        if option == 'b':
            break

        options_dict[option]()

    # input("HERE")
    # while True:
    #     
    #     input("HERE")
    #     option = Utils.endless_terminal(table, *list(options_dict.keys()), clear="yes")
        
    #     if option == 'b':
    #         break


# Method to control the flow of a selected channel
# + Selecet a field
# + Remove the channel
def channel_menu(ts, user_api_key, i, indexes, channel_name):
    channel = Channel(user_api_key, i, indexes[i], channel_name)
    pattern = re.compile(r"^[1-8]$")
    str_field_list_commands_help = "create field\tTo create a new field. Up to 8 fields in total.\n" \
                                                "clear fields\tClear all the data from all the fields.\n" \
                                                "delete field\tDelete a existing field.\n" \
                                                "delete all fields\tDelete all existing field and their data.\n"

    options_dict = {
                    "create field": channel.create_one_field,
                    "clear fields": channel.clear_data_from_all_fields,
                    "delete field": channel.delete_one_field,
                    "delete all fields": channel.delete_all_fields
                }

    while True:
        option = channel.channel_menu(channel.index, channel.channel_dict)

        if option == 'b':
            break
        elif option == '2':
            while True:

                o = channel.print_channel_fields()

                if o == 'b':
                    break
                
                if o == 'refresh':
                    continue

                valid_options = list(options_dict.keys()) + channel.valid_field_indexes

                field_menu_option = Utils.endless_terminal(channel.table_of_fields, *valid_options, help_message=str_field_list_commands_help, menu=channel.channel_name)

                if field_menu_option == 'b':
                    break

                # field has been selected
                if pattern.match(field_menu_option):
                    field_menu(ts, channel, field_menu_option, channel.get_field_name(int(field_menu_option)))

                # option in field list has been selected (help, create field, delete field, ...)
                if field_menu_option in options_dict:
                    options_dict[field_menu_option]()

        elif option == 'delete':
            ts.get_account_info()
            break


# ThingSpeak menu Method
def main_menu(user_api_key):
    ts = ThingSpeak(user_api_key)

    while True:
        if ts.hayCanales:
            str_banner = "1 -- Ver canales públicos.\n\n" \
                        "2 -- Ver canales privados.\n\n" \
                        "3 -- Ver todos los canales.\n\n" \
                        "4 -- Create a new channel.\n\n" \

            option = Utils.endless_terminal(str_banner, "1", "2", "3", "4", clear="yes")

            if option.__eq__("b"):
                signal_handler()

            if option == "1":
                indexes = ts.print_channel_index(ts.public_channels)
            elif option == "2":
                indexes = ts.print_channel_index(ts.private_channels)
            elif option == "3":
                indexes = ts.print_channel_index(ts.all_channels)
            elif option == "4":
                ts.create_channel(user_api_key)
                ts.get_account_info()
                continue

            i = Utils.endless_terminal("\nSelect a channel.\nOr enter \"b\" to go backwards.", *indexes.keys())

            if i.__eq__('b'):
                continue

            channel_menu(ts, user_api_key, i, indexes, ts.get_channel_name(int(i)))
        else:
            i = Utils.endless_terminal("You dont have any channels in this account.\nDo you want to create one? [y/n] ",
                                tty=False)
            if i.__eq__("y"):
                ts.create_channel(user_api_key)
                ts.get_account_info()


if __name__ == '__main__':
    main_menu("0WX1WIYR7G3QMKUR")
