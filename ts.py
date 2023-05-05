from inventory import devices
from netmiko import ConnectHandler
from backups import router_check

options = {
    "1" : "Show interfaces.",
    "2" : "Show version.",
    "3" : "Show running-config.",
    "4" : "show ip route.",
    "5" : "show access-lists.",
    "6" : "Quit from the troubleshooting menu."
}

def host_query():
    router_input = input("To which router should I connect (R1 - R4): ").upper()
    hostname = router_check(router_input)
    if isinstance(hostname, int):
        return hostname
    else:
        print("Wrong hostname\n")
        return host_query()

def dev_connect():
    router_input = host_query()
    return ConnectHandler(**devices[router_input])

def send_command(command):
    connect = dev_connect()
    output = connect.send_command(command)
    print("\n")
    print(output)
    print("\n")
    connect.disconnect()

def ts_query():
    option = ""
    
    print("Troubleshooting menu")
    while option != "6":
        for key, value in options.items():
            print(key + ") " + value)
        option = input("Choose an option: ")
        if option == "1":
            input_command = "sh ip int brief"
            send_command(input_command)
        elif option == "2":
            input_command = "sh version"
            send_command(input_command)
        elif option == "3":
            input_command = "sh run"
            send_command(input_command)
        elif option == "4":
            input_command = "sh ip route"
            send_command(input_command)
        elif option == "5":
            input_command = "sh ip access-lists"
            send_command(input_command)
        elif option == "6":
            print("Exitting.")
            break
        else:
            print("Enter a correct option.\n")

ts_query()
