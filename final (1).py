import asyncio
import json
import socket
from asyncio import DatagramTransport
import threading
from typing import Tuple
# from sensor import start_sensor_data_generation
import random
import argparse




def generate_health_status(udp):
    if udp.vehicle_name not in udp.sensor:
        udp.sensor[udp.vehicle_name] = {}

    # Update or add the 'temperature' key
    udp.sensor[udp.vehicle_name]["health"] = [str(random.randint(0, 100)), 5]
    # print("random data: ",str(random.randint(-10, 40)))


def generature_pressure(udp):
    if udp.vehicle_name not in udp.sensor:
        udp.sensor[udp.vehicle_name] = {}

    # Update or add the 'temperature' key
    udp.sensor[udp.vehicle_name]["pressure"] = [str(random.randint(900, 1100)), 5]
    # udp.sensor[udp.vehicle_name] = {}
    # udp.sensor[udp.vehicle_name]["pressure"]=[str(random.randint(900, 1100)),25]


def generate_gps_position(udp):
    if udp.vehicle_name not in udp.sensor:
        udp.sensor[udp.vehicle_name] = {}

    # Update or add the 'temperature' key
    udp.sensor[udp.vehicle_name]["position"] = [
        str(random.randint(-9000, 9000) / 100) + ',' + str(random.randint(-9000, 9000) / 100), 5]

    # return str(random.randint(-9000, 9000) / 100) + ',' + str(random.randint(-9000, 9000) / 100)


def generate_humidity(udp):
    if udp.vehicle_name not in udp.sensor:
        udp.sensor[udp.vehicle_name] = {}

    # Update or add the 'temperature' key
    udp.sensor[udp.vehicle_name]["humidity"] = [str(random.uniform(-2, 2)), 5]


async def generate_data(sensorType, udp):
    while True:
        for i in sensorType:
            if i == 'health':
                generate_health_status(udp)
            if i == "position":
                generate_gps_position(udp)

            if i == 'pressure':
                generature_pressure(udp)
            if i == 'humidity':
                generate_humidity(udp)
        await asyncio.sleep(5)


class _Address:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def __eq__(self, other):
        return self.host == other.host and self.port == other.port

    def __hash__(self):
        return hash((self.host, self.port))

    def __str__(self):
        return f"{self.host}:{self.port}"


class UDP:
    def __init__(self, network, name, port) -> None:
        self.udp_port = port
        self.udp_local_port = self.udp_port + 1
        self.tcp_port = self.udp_port + 200
        self.network = network
        self.vehicle_name = name
        self.hostname = socket.gethostbyname(socket.gethostname())
        self.fib = {}
        self.sensor = {}
        self.announcement = {
            "heartbeat": "ALIVE",
            "NEIGHBOURS": self.hostname,
            "vehicle_name": self.vehicle_name,
            "network": self.network,
            "port": self.tcp_port
        }

    async def start_udp(self):
        # Listen for announcements
        class Protocol:
            def connection_made(_, transport: DatagramTransport):
                print(f"UDP transport established: {transport}")

            def connection_lost(_, e: Exception):
                print(f"UDP transport lost: {e}")

            def datagram_received(_, data: bytes, addr: Tuple[str, int]):
                self._on_udp_data(data, _Address(*addr[0:2]))

            def error_received(_, e: OSError):
                print(f"UDP transport error: {e}")

        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(lambda: Protocol(),
                                                                  local_addr=("0.0.0.0", self.udp_port),
                                                                  allow_broadcast=True)

        # Regularly broadcast announcements
        while True:
            print("Sending peer announcement...")
            transport.sendto(json.dumps(self.announcement).encode('utf-8'), ("255.255.255.255", self.udp_port))
            await asyncio.sleep(20)

    def _on_udp_data(self, data: bytes, addr: _Address):
        # print(f"Received data {data=}")
        self.add_to_fib(data, addr)
        print(self.fib)
        print(self.sensor)

    def add_to_fib(self, data: bytes, addr: _Address):
        # Decode the bytes data to string and parse it as JSON
        data_string = data.decode('utf-8')
        try:
            data_dict = json.loads(data_string)
            name = data_dict['vehicle_name']
            network = data_dict['network']
            host = addr.host
            port = data_dict['port']
            ttl = 25
            value = {}
            value[name] = [host, port, ttl]

            # Update TTL if the entry exists, else add a new entry
            # if name in self.fib:
            #     self.fib[network][name][2] = ttl
            # else:
            #     self.fib[network] = value
            if network in self.fib.keys():
                if name in self.fib[network].keys():
                    self.fib[network][name][2] = ttl
                else:
                    self.fib[network].update({name: value[name]})
            else:
                self.fib[network] = {name: value[name]}
        except json.JSONDecodeError as e:
            import traceback
            print(traceback.format_exc())
            print(f"Error decoding JSON data: {e}")
        except KeyError as e:
            import traceback
            print(traceback.format_exc())
            print(f"Key error: {data_string} does not contain a vehicle_name")

    def decision_make(sensor_type, data):
        if sensor_type == "health":
            if data < 30:
                print("Health declining ALERT!")

        else:
            print("ignore")
    async def decrement_ttl(self):
        while True:
            try:
                for key in list(self.fib.keys()):
                    for val in self.fib[key]:
                        # Decrement the TTL
                        self.fib[key][val][2] -= 1
                        # Remove the entry if the TTL reaches zero
                        if self.fib[key][val][2] <= 0:
                            del self.fib[key][val]
                for key in list(self.sensor.keys()):
                    for val in self.sensor[key]:
                        # Decrement the TTL
                        self.fib[key][val][1] -= 1
                        # Remove the entry if the TTL reaches zero
                        if self.fib[key][val][1] <= 0:
                            del self.fib[key][val]
            except Exception:
                pass
            # Wait for 1 second before decrementing again
            await asyncio.sleep(1)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        print(f"(handle_client) Received connection from {addr}")

        while True:
            data = await reader.read(100)
            if not data:
                break

            message = data.decode('utf-8')
            network = message.split('/')[0]
            name = message.split('/')[1]
            sensor_type = message.split('/')[2]
            print(f"(handle_client) Received {message} from {addr}")
            if name not in self.sensor.keys():
                if network == self.network and (network in list(self.fib.keys())):
                # print(name)
                # host = '127.0.0.1'
                    host = socket.gethostbyname(socket.gethostname())
                    port = self.fib[network][name][1]
                #port = list(self.fib[network][list(self.fib[network].keys())[0]])[1]
                    response = await self.send_request(host, port, message)
                # self.sensor[name][sensor_type] = response
                elif network != self.network and (network in list(self.fib.keys())):
                    host=list(self.fib[network][list(self.fib[network].keys())[0]])[0]
                    port = list(self.fib[network][list(self.fib[network].keys())[0]])[1]
                    response = await self.send_request(host, port, message)
                else:
                    break
            else:
                response = self.sensor[name][sensor_type][0]
            # response = "Hi"
            response = response.encode('utf-8')
            writer.write(response)
            await writer.drain()

        print(f"Closing connection with {addr}")
        writer.close()
        await writer.wait_closed()

    # async def handle_sensor_data(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    #     data = await reader.read(100)  # Read up to 100 bytes
    #     message = data.decode('utf-8')
    #     addr = writer.get_extra_info('peername')

    #     print(f"Received {message} from {addr}")

    #     # store_to_repo(message)
    #     self.sensor[self.vehicle_name]={message["name"]:[message["value"],message["ttl"]]}

    #     # You can process the sensor data here
    #     # ...

    #     # Close the connection
    #     print("Close the connection")
    #     writer.close()

    async def start_tcp_server(self):
        server = await asyncio.start_server(
            self.handle_client, self.hostname, self.tcp_port)
        addr = server.sockets[0].getsockname()
        print(f'Serving (start_tcp_server) on {addr}')

        async with server:
            await server.serve_forever()

    # async def start_sensor_server(self):
    #     server = await asyncio.start_server(self.handle_sensor_data, '127.0.0.1', self.sensorport)
    #     addr = server.sockets[0].getsockname()
    #     print(f"Serving on {addr}")

    #     async with server:
    #         await server.serve_forever()

    async def send_request(self, host, port, message):
        print(f"Sending request to {host}:{port}...")
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(message.encode('utf-8'))
        await writer.drain()

        response = await reader.read(100)  # Read the response
        print(f"Received response from {host}:{port}: {response.decode('utf-8')}")

        writer.close()
        await writer.wait_closed()

        return response.decode()


async def tcp_client(message, host, port, retry_interval=5):
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)

            print(f'Sending: {message}')
            writer.write(message.encode())

            data = await reader.read(100)
            print(f'Received: {data.decode()}')

            print('Closing the connection')
            writer.close()
            await writer.wait_closed()

            break  # Exit the loop after successful communication

        except (ConnectionRefusedError, OSError) as e:
            print(f"Connection to {host}:{port} refused, retrying in {retry_interval} seconds...")
            await asyncio.sleep(retry_interval)
        except Exception as e:
            print(f"An error occurred: {e}, retrying in {retry_interval} seconds...")
            await asyncio.sleep(retry_interval)


# def run_command_loop(udp, loop):
#     while True:
#         command = input("Enter command (send, quit): ").strip().lower()
#         if command == "send":
#             request_data = input("Enter interest package (eg. network2/bus1/temperature): ").strip().lower()
#             vehicle_name = request_data.split('/')[1]
#             network = request_data.split('/')[0]
#             if network == udp.network and (network in list(udp.fib.keys())):
#                 if vehicle_name in list(udp.fib[network].keys()):  ## if network1 = fib[0] & bus1=fib[1]
#                     # host= udp.fib[network][vehicle_name][0] # portnumber = fib[1]
#                     # host='127.0.0.1'
#                     host = udp.hostname
#                     port = udp.fib[network][vehicle_name][1]
#                 else:
#                     print("Vehicle name doesn't exist")
#                     continue
#             elif network != udp.network and (network in list(udp.fib.keys())):
#                 vehicle_name =list(udp.fib[network].values())[0]
#                 host= vehicle_name[0]
#                 port=vehicle_name[1]
#                 host=host.split('.')[3]
#                 host=f'rasp-0{host}.berry.scss.tcd.ie'
#             else:
#                 print("Network doesn't exist")
#                 continue

#             asyncio.run_coroutine_threadsafe(udp.send_request(host, port, request_data), loop)
#         elif command == "quit":
#             break
#         else:
#             continue
def run_command_loop(udp, loop):
    while True:
        command = input("Enter command (send, quit): ").strip().lower()
        if command == "send":
            request_data = input("Enter interest package (eg. network2/bus1/temperature): ").strip().lower()
            vehicle_name = request_data.split('/')[1]
            network = request_data.split('/')[0]
            sensor_type=request_data.split('/')[2]
            if network == udp.network and (network in list(udp.fib.keys())):
                if vehicle_name in list(udp.fib[network].keys()):  ## if network1 = fib[0] & bus1=fib[1]
                    # host= udp.fib[network][vehicle_name][0] # portnumber = fib[1]
                    # host='127.0.0.1'
                    host = udp.hostname
                    port = udp.fib[network][vehicle_name][1]
                    future=asyncio.run_coroutine_threadsafe(udp.send_request(host, port, request_data), loop)
                    response = future.result(timeout=10)
                    print("Data =", response)
                else:
                    print("Vehicle name doesn't exist")
                    continue
            elif network != udp.network and (network in list(udp.fib.keys())):
                try:
                    vehicle_name = list(udp.fib[network].values())[0]
                    host = vehicle_name[0]
                    port = vehicle_name[1]
                    host = host.split('.')[3]
                    host = f'rasp-0{host}.berry.scss.tcd.ie'
                    future=asyncio.run_coroutine_threadsafe(udp.send_request(host, port, request_data), loop)
                    response = future.result(timeout=10)
                    print("Data =", response)
                    #actuator(response,sensor_type)
                except:
                    #host = list(udp.fib[udp.network][list(udp.fib[udp.network].keys())[1]])[0]
                    host = udp.hostname
                    port = list(udp.fib[udp.network][list(udp.fib[udp.network].keys())[1]])[1]
                    future=asyncio.run_coroutine_threadsafe(udp.send_request(host, port, request_data), loop)
                    response = future.result(timeout=10)
                    print("Data =",response)
            else:
                # if vehicle_name in list(udp.fib[udp.network].keys()):
                #     host = udp.hostname
                #     port = udp.fib[udp.network][vehicle_name][1]
                # else:
                print("Network doesn't exist")
                continue

        elif command == "quit":
            break
        else:
            continue


class ListenerProtocol(asyncio.DatagramProtocol):
    def __init__(self, udp_obj) -> None:
        self.udp_obj = udp_obj
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        print(f"ListeningProtocol on {self.transport.get_extra_info('sockname')}")

    def datagram_received(self, data, addr):
        self.udp_obj.add_to_fib(data, _Address(*addr[0:2]))
        # print(f"Datagram Received: {data.decode()} from {addr}")


async def receive_send_local(udp, sendports):
    loop = asyncio.get_running_loop()

    # Create one listening transport
    listen_transport, _ = await loop.create_datagram_endpoint(
        lambda: ListenerProtocol(udp_obj=udp),
        local_addr=('127.0.0.1', udp.udp_local_port))

    # Create sender transport and protocol only once
    sender_transport, sender_protocol = await loop.create_datagram_endpoint(
        lambda: asyncio.DatagramProtocol(),
        local_addr=('127.0.0.1', 0))  # A random outgoing port is fine

    try:
        print("Sending peer announcements...")
        while True:
            # message = f"Hello from Node {udp.vehicle_name}"
            announcement = {
                "heartbeat": "ALIVE",
                "NEIGHBOURS": udp.hostname,
                "vehicle_name": udp.vehicle_name,
                "network": udp.network,
                "port": udp.tcp_port
            }
            for port in sendports:
                sender_transport.sendto(json.dumps(announcement).encode('utf-8'), ('127.0.0.1', port))
            await asyncio.sleep(5)

    finally:
        # Close the transports
        listen_transport.close()
        sender_transport.close()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Enter Port for Global UDP broadcast', type=int)
    parser.add_argument('--name', help='Enter Name for Device', type=str)
    parser.add_argument('--network', help='Enter Name for Network', type=str)

    args = parser.parse_args()
    if args.port is None:
        print("Please specify the CNN model to use")
        exit(1)
    if args.name is None:
        print("Please specify the CNN model to use")
        exit(1)
    if args.network is None:
        print("Please specify the CNN model to use")
        exit(1)
    udp = UDP(args.network, args.name, args.port)
    sensors = ['health', 'position']
    sensor_task = asyncio.create_task(generate_data(sensors, udp))
    # sendports = [33002,33004]
    sendports = list(range(33002, 33020, 2))
    sendports.remove(args.port + 1)

    client_task = asyncio.create_task(udp.start_udp())
    local_client_task = asyncio.create_task(receive_send_local(udp, sendports))
    server_task = asyncio.create_task(udp.start_tcp_server())
    ttl_task = asyncio.create_task(udp.decrement_ttl())
    # sensor_task=asyncio.create_task(udp.start_sensor_server())

    # Get the current event loop for the main thread
    loop = asyncio.get_running_loop()

    # Start the command loop in a separate thread, passing the event loop
    command_thread = threading.Thread(target=run_command_loop, args=(udp, loop), daemon=True)
    command_thread.start()

    try:
        await asyncio.gather(client_task, local_client_task, server_task, ttl_task, sensor_task)
        # await asyncio.gather(client_task, local_client_task, server_task, ttl_task)
    except asyncio.CancelledError:
        # The server task has been cancelled, meaning we're shutting down
        pass


# Run the event loop
asyncio.run(main())

# network2|rover2|temperature
# network2/rover2/health