# interface_manager/views.py

from django.shortcuts import render, redirect
from django.conf import settings
from ncclient import manager
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import AuthenticationError
from .forms import ConnectForm
from lxml import etree

# Global manager instance
global_manager = None

def create_network_interface(interface_name):
    rpc_request = f'''
    <create-network-interface xmlns="http://example.com/aselsan-network-settings">
        <interface-name>{interface_name}</interface-name>
    </create-network-interface>
    '''

    if global_manager is None or not global_manager.connected:
        # Try to connect using saved session data
        try:
            global_manager = manager.connect(
                host=settings.NETOPEER_HOST,
                port=settings.NETOPEER_PORT,
                username=settings.NETOPEER_USERNAME,
                password=settings.NETOPEER_PASSWORD,
                hostkey_verify=False
            )
        except Exception as e:
            return f"Error connecting to Netopeer server: {str(e)}"

    try:
        response = global_manager.dispatch(etree.fromstring(rpc_request))
        return f"RPC response: {response}"
    except Exception as e:
        return f"Error sending RPC: {str(e)}"

def set_ip_settings(interface_name, ip_address):
    rpc_request = f'''
    <set-ip-settings xmlns="http://example.com/aselsan-network-settings">
        <interface-name>{interface_name}</interface-name>
        <ip-address>{ip_address}</ip-address>
    </set-ip-settings>
    '''

    if global_manager is None or not global_manager.connected:
        # Try to connect using saved session data
        try:
            global_manager = manager.connect(
                host=settings.NETOPEER_HOST,
                port=settings.NETOPEER_PORT,
                username=settings.NETOPEER_USERNAME,
                password=settings.NETOPEER_PASSWORD,
                hostkey_verify=False
            )
        except Exception as e:
            return f"Error connecting to Netopeer server: {str(e)}"

    try:
        response = global_manager.dispatch(etree.fromstring(rpc_request))
        return f"RPC response: {response}"
    except Exception as e:
        return f"Error sending RPC: {str(e)}"

def create_interface(request):
    if request.method == 'POST':
        interface_name = request.POST.get('interface_name')
        response = create_network_interface(interface_name)
        return render(request, 'interface_response.html', {'response': response})

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
