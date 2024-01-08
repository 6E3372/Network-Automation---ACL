#
# Title: Automate ACL using Python
#
# pip install netmiko
#

from netmiko import ConnectHandler
import time

banner = '''

 ▄▄▄      ▄▄▄       ▄████▄   ██▓          ██▓███ ▓██   ██▓
▒████▄   ▒████▄    ▒██▀ ▀█  ▓██▒         ▓██░  ██▒▒██  ██▒
▒██  ▀█▄ ▒██  ▀█▄  ▒▓█    ▄ ▒██░         ▓██░ ██▓▒ ▒██ ██░
░██▄▄▄▄██░██▄▄▄▄██ ▒▓▓▄ ▄██▒▒██░         ▒██▄█▓▒ ▒ ░ ▐██▓░
 ▓█   ▓██▒▓█   ▓██▒▒ ▓███▀ ░░██████▒ ██▓ ▒██▒ ░  ░ ░ ██▒▓░
 ▒▒   ▓▒█░▒▒   ▓▒█░░ ░▒ ▒  ░░ ▒░▓  ░ ▒▓▒ ▒▓▒░ ░  ░  ██▒▒▒ 
  ▒   ▒▒ ░ ▒   ▒▒ ░  ░  ▒   ░ ░ ▒  ░ ░▒  ░▒ ░     ▓██ ░▒░ 
  ░   ▒    ░   ▒   ░          ░ ░    ░   ░░       ▒ ▒ ░░  
      ░  ░     ░  ░░ ░          ░  ░  ░           ░ ░     
                   ░                  ░           ░ ░     
                      
Coded by:n3r,Ad3n,hyc4rl,boredzz    

'''

def main_menu():
    print(banner)
    router_ip = input("Enter router IP address: ")
    return router_ip

def authentication_menu():
    choice = input("Choose authentication method:\n1. Default username and password\n2. Manual username and password\nEnter choice (1/2): ")
    return choice

def manual_authentication():
    manual_username = input("Enter manual username: ")
    manual_password = input("Enter manual password: ")
    return manual_username, manual_password

def establish_ssh_connection(router_ip, use_default_credentials=True, manual_username="", manual_password=""):
    if use_default_credentials:
        username = "admin"
        password = "admin"
    else:
        username = manual_username
        password = manual_password

    device = {
        'device_type': 'cisco_ios',
        'ip': router_ip,
        'username': username,
        'password': password,
        'secret': password,
        'verbose': True,
    }

    # Connect to the router
    ssh_conn = ConnectHandler(**device)
    ssh_conn.enable()

    # Send enable and configure terminal commands
    enable_commands = [
        'enable',
        'configure terminal',
    ]
    ssh_conn.send_config_set(enable_commands)
    time.sleep(1)

    return ssh_conn

# Standard ACL Configuration
def configure_standard_acl(ssh_conn, acl_number, source_ip, wildcard_mask_source, action):
    config_commands = [
        f'access-list {acl_number} {action} {source_ip} {wildcard_mask_source}',
        'exit',
    ]

    output = ssh_conn.send_config_set(config_commands)
    print(output)

# Extended ACL Configuration
def configure_extended_acl(ssh_conn, acl_number, source_ip, destination_ip, wildcard_mask_source, wildcard_mask_dest, action):
    config_commands = [
        f'access-list {acl_number} {action} {protocol} {source_ip} {wildcard_mask_source} {destination_ip} {wildcard_mask_dest}',
        'exit',
    ]

    output = ssh_conn.send_config_set(config_commands)
    print(output)

# Apply ACL to interface
def apply_acl_to_interface(ssh_conn, interface, acl_number, direction):
    config_commands = [
        f'interface {interface}',
        f'ip access-group {acl_number} {direction}',
        'exit',
    ]

    output = ssh_conn.send_config_set(config_commands)
    print(output)

# show access-list command
def show_acl(ssh_conn):
    output = ssh_conn.send_command("show access-list")
    print(output)

# close ssh connection
def close_ssh_connection(ssh_conn):
    ssh_conn.disconnect()

if __name__ == "__main__":
    router_ip = main_menu()

    
    choice = authentication_menu()

    if choice == "2":
        manual_username, manual_password = manual_authentication()
        # Establish SSH connection
        ssh_conn = establish_ssh_connection(router_ip, use_default_credentials=False, manual_username=manual_username, manual_password=manual_password)

    else:
         ssh_conn = establish_ssh_connection(router_ip)
        

    # Number of ACL to be configure
    num_acls = int(input("Enter the number of ACLs to configure: "))
    for _ in range(num_acls):
        # ACL details
        acl_number = input("Enter ACL number: ")
        source_ip = input("Enter source IP address: ")
        wildcard_mask_source = input("Enter wildcard mask for source: ")
        

        acl_number = int(acl_number)

        if (100 <= acl_number <=199) or (2000 <= acl_number <= 2699):
            destination_ip = input("Enter destination IP address: ")
            wildcard_mask_dest = input("Enter wildcard mask for destination: ")
            action = input("Enter action (permit/deny): ")
            protocol = input("Enter protocol (tcp/udp/icmp): ")
            port = input("Enter port: ")

            configure_extended_acl(ssh_conn, acl_number, source_ip, destination_ip, wildcard_mask_source, wildcard_mask_dest)

            # Apply ACL on interface
            interface =  input("Enter interface to apply ACL (e.g., GigabitEthernet0/0): ")
            direction = input("Enter the direction (in/out)").lower()

            apply_acl_to_interface(ssh_conn, interface, acl_number, direction)


        elif (1 <= acl_number <= 99) or (1300 <= acl_number <= 1999):
            action = input("Enter action (permit/deny): ")
            configure_standard_acl(ssh_conn, acl_number, source_ip, wildcard_mask_source, action)

           # Apply ACL on interface
            interface =  input("Enter interface to apply ACL (e.g., GigabitEthernet0/0): ")
            direction = input("Enter the direction (in/out)").lower()

            apply_acl_to_interface(ssh_conn, interface, acl_number, direction)
        else:
            print("Invalid ACL type. This script only supports Standard and Extended ACL only!")

    # Show configured ACL(s)
    show_acl(ssh_conn)

    # Close the SSH connection
    close_ssh_connection(ssh_conn)




