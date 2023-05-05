REGEX_PATTERN = r"^[R][1-4]$"
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from datetime import datetime
from inventory import devices
import re

#Takes current time for backup
today_date = datetime.now()
today_date = today_date.strftime("%d-%m-%Y_%H-%M-%S")

options = {
    "1": "Take a backup.",
    "2": "Restore a backup.",
    "3": "Compare backups.",
    "4": "Quit from the configuration menu."
}

backup_settings = {
    "1": "Take it from all devices.",
    "2": "Take it from a specific device."
}

def host_query():
    router_input = input("To which router should I connect (R1 - R4): ").upper()
    hostname = router_check(router_input)
    if isinstance(hostname, int):
        return hostname
    else:
        print("Wrong hostname\n")
        return host_query()

def router_check(choice):
    if re.match(REGEX_PATTERN, choice):

        # Remove R, so we can take the digit and sub 1 to use list indexing R4 = devices[3], R3 = devices[2]
        choice = choice.replace("R", '') 
        choice = int(choice)
        return choice - 1
        
def take_backup(device):
    try:
        connect = ConnectHandler(**device)
        hostname = connect.find_prompt()
        print(hostname)
        hostname= hostname.replace("#", '')
        command = "copy running-config ftp: "
        output = connect.send_command(command,
                expect_string=r"Address")
        if "Address" in output:
            output += connect.send_command_timing(
                    command_string="192.168.0.108",
                    strip_prompt=False,
                    strip_command=False)
        if "Destination" in output:
                output += connect.send_command_timing(
                    command_string=f"{hostname}.{today_date}.txt",
                    strip_prompt=False,
                    strip_command=False)
        connect.disconnect()

        #Timeout error handling
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error: 
        print(f"Oops, we have an error: {error}")
    print(output)


def backup_options():
    for key, value in backup_settings.items():
        print(key + ") " + value)

    option = input("Choose an option: ")
    if option in backup_settings:

        #Takes backup from all of the devices
        if option == "1": 
            for device in devices:
                    take_backup(device)
            
        #Takes backup from a specific device  TESTS
        elif option == "2": 
            choice = host_query()
            take_backup(devices[router_check(choice)])
    else:
        print("Wrong option.")
        return backup_options()

#Device information prompt
def backup_restore():
    restore_choice = input("Choose a device from R1 - R4: ").upper()
    try:
        if re.match(REGEX_PATTERN, restore_choice):

            # Remove R, so we can take the digit and sub 1 to use list indexing R4 = devices[3], R3 = devices[2]
            restore_choice = restore_choice.replace("R", '') 
            restore_choice = int(restore_choice)
            restore_device(devices[restore_choice - 1])
        else:
            print("\nWrong hostname entered, try again.")
            return backup_restore()

    except ValueError as e:
        print(f"Oops, value error: {e}.")


#Actual restore from a file
def restore_device(device):
    file_path = input("Enter the absolute path of the file: ")
    connect = ConnectHandler(**device)
    output = connect.send_config_from_file(config_file = file_path)
    print(output)

    #Checks whether to save the config
    save_run = input("Do you want to save the running config [y/n]: ").lower()
    if save_run == 'y':
        print(connect.save_config())
    elif save_run == 'n':
        print("\n")
    else:
        print("\nThe running config is not saved, but the configuration was sent!!!")

def backups_comparison(): # fix
    is_same = True
    file_1 = input("Enter the absolute path to the first backup: ")
    file_2 = input("Enter the absolute path to the second backup: ")

    backup_1 = open(file_1, "r")
    backup_2 = open(file_2, "r")
    lines = backup_1.readlines()
    for i, lines2 in enumerate(backup_2):
        if lines2 != lines[i]:
            is_same = False
            n = i
            #print(lines[i - 1])
            while lines[i - 1].strip() != "!":
               print(lines[i - 1].strip())
               i -= 1
            print(f"\nBackup 1 has {lines[n]}.")
            print(f"Backup 2 has {lines2}.\n")
            
    if is_same == True:
        print("\nThe files are the same.")
            
#Asks which action should it perform
def restore_query(): 
    option = ""
    print("Backup menu")
    while option != "4":
        for key, value in options.items():
            print(key + ") " + value)
        option = input("Choose an option: ")
        if option == "1":
            backup_options()
        elif option == "2":
            backup_restore()
        elif option == "3":
            backups_comparison()
        elif option == "4":
            print("Exitting.")
            break
        else:
            print("Enter a correct option.\n")