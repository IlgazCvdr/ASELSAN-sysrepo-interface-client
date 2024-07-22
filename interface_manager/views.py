# interface_manager/views.py

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from ncclient import manager
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import AuthenticationError
from .forms import ConnectForm
from lxml import etree

# Global manager instance
global_manager = None


def get_network_interfaces(request):
    global global_manager
    connection_data = request.session.get('netopeer_connection')

    if not connection_data:
        return HttpResponse("Connection data not found in session", status=400)

    if not global_manager:
        try:
            global_manager = manager.connect(
                host=connection_data['host'],
                port=connection_data['port'],
                username=connection_data['username'],
                password=connection_data['password'],
                hostkey_verify=False
            )
        except AuthenticationError:
            return HttpResponse("Authentication failed", status=403)
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}", status=500)

    if request.method == 'POST':
        interface_name = request.POST.get('interface_name')
        ip_address = request.POST.get('ip_address')

        rpc_request = f'''
        <set-ip-settings xmlns="http://example.com/aselsan-network-settings">
            <interface-name>{interface_name}</interface-name>
            <ip-address>{ip_address}</ip-address>
        </set-ip-settings>
        '''
        try:
            response = global_manager.dispatch(etree.fromstring(rpc_request))
            print(response)
        except Exception as e:
            return HttpResponse(f"Error sending RPC: {str(e)}", status=500)
    
    try:
        # Send the RPC request to get interfaces
        print("aaaaaaaaaa")
        rpc_request = '''
    <get-network-interfaces xmlns="http://example.com/aselsan-network-settings"/>'''
        response = global_manager.dispatch(etree.fromstring(rpc_request))
        print(response)
        interfaces = parse_interfaces_response(response)
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)
    
    return render(request, 'network_interfaces.html', {'interfaces': interfaces})

def parse_interfaces_response(response):
    interfaces = []
    root = etree.fromstring(response.xml)
    interfaces_text = root.findtext('.//{http://example.com/aselsan-network-settings}interfaces').strip()
    
    lines = interfaces_text.split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) == 2:
            name, ip = parts
            interfaces.append({'name': name, 'ip': ip})
    
    return interfaces


def create_interface(request):
    global global_manager
    if request.method == 'POST':
        interface_name = request.POST.get('interface_name')
        ip_address = request.POST.get('ip_address')
        connection_data = request.session.get('netopeer_connection')

        if not connection_data:
            return HttpResponse("Connection data not found in session", status=400)

        if not global_manager:
            try:
                global_manager = manager.connect(
                    host=connection_data['host'],
                    port=connection_data['port'],
                    username=connection_data['username'],
                    password=connection_data['password'],
                    hostkey_verify=False
                )
            except AuthenticationError:
                return HttpResponse("Authentication failed", status=403)
            except Exception as e:
                return HttpResponse(f"An error occurred: {e}", status=500)

        # Create the interface
        create_rpc_request = f'''
            <create-network-interface xmlns="http://example.com/aselsan-network-settings">
                <interface-name>{interface_name}</interface-name>
            </create-network-interface>
            '''
        try:
            response = global_manager.dispatch(etree.fromstring(create_rpc_request))
        except Exception as e:
            return HttpResponse(f"Error creating interface: {str(e)}", status=500)

        # Set the IP address
        set_ip_rpc_request = f'''
            <set-ip-settings xmlns="http://example.com/aselsan-network-settings">
                <interface-name>{interface_name}</interface-name>
                <ip-address>{ip_address}</ip-address>
            </set-ip-settings>
            '''
        try:
            response = global_manager.dispatch(etree.fromstring(set_ip_rpc_request))
        except Exception as e:
            return HttpResponse(f"Error setting IP address: {str(e)}", status=500)

        return redirect('network_interfaces')

    return render(request, 'create_interface.html')

def connect(request):
    global global_manager

    if request.method == 'POST':
        form = ConnectForm(request.POST)
        if form.is_valid():
            host = form.cleaned_data['host']
            port = form.cleaned_data['port']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                global_manager = manager.connect(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    hostkey_verify=False,
                    allow_agent=False,
                    look_for_keys=False,
                    device_params={'name': 'default'}
                )

                # Store necessary data in session
                request.session['netopeer_connection'] = {
                    'host': host,
                    'port': port,
                    'username': username,
                    'password': password
                }

                return redirect('create_interface')

            except TimeoutExpiredError:
                error_message = f"Connection to {host}:{port} timed out."
                return render(request, 'connect.html', {'form': form, 'error_message': error_message})

            except AuthenticationError:
                error_message = f"Authentication failed for {username} on {host}:{port}."
                return render(request, 'connect.html', {'form': form, 'error_message': error_message})

            except Exception as e:
                error_message = f"Error connecting to {host}:{port}: {str(e)}"
                return render(request, 'connect.html', {'form': form, 'error_message': error_message})

    else:
        form = ConnectForm()

    return render(request, 'connect.html', {'form': form})
