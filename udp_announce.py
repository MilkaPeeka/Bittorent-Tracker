import aioudp
import asyncio
import struct
import random
import string
import datetime
from socket import inet_aton
from logs_handler import LogHandler
from announce_log import AnnounceLog
import socket

lh = LogHandler("logs.db")
PROT_ID = 0x41727101980
def parse_announce_struct(payload):
    # this is what we get when someone announces to us
    # 8 bytes conn_id
    # 4 bytes action. will be 1 for announce
    # 4 bytes trans_id
    # 20 byte array of info hash
    # 20 bytes peer_id
    # 8 bytes downloaded
    # 8 bytes left
    # 8 bytes uploaded
    # 4 bytes event 
    # 4 bytes ip (0 to use sender id)
    # 4 bytes random key
    # 4 bytes numwant (-1 for client to decide)
    # 2 bytes port were listening on
    # 4 bytes extenstions
    # 1 byte padding
    return struct.unpack("! q i 4s 20s 20s q q q i i i i H i x", payload)


def on_msg(settings, payload, addr):
    conn_id, action, trans_id, info_hash, peer_id, downloaded, left, uploaded, event, ip, rand_key, numwant, port, extensions = parse_announce_struct(payload)

    if ip == 0:
        ip = addr[0]

    announcer_torrent_addr = (ip, port)
    selected_torrent = None
    for torrent in lh.get_torrents():
        if torrent.info_hash == info_hash:
            selected_torrent = torrent
            print("found torrent")
            break


    if selected_torrent == None:
        return None
    
    match event:
        case 2:
            event = "start"
        case 3:
            event = "stop"
        case 1:
            event = "finish"
        case 0:
            event = "resume"

    # now we have all the data needed, we have the torrent we need. We just need to update the torrent data and then return peer list to the user

    log = AnnounceLog(datetime.datetime.now(), ip, port, event, downloaded, uploaded)

    torrent.add_announcement(log)

    # after we saved the log we can now send a response

    response_to_announcer = construct_response(settings, trans_id, torrent, announcer_torrent_addr)

    return response_to_announcer

def construct_response(settings, trans_id, torrent, announcer_torrent_addr):
    # we need to return interval, seeders, leechers and peer_list

    peers = torrent.get_peers() # a set where each entry is {ip, port}
    addr_list = []
    for peer in peers:
        if peer == announcer_torrent_addr:
            continue
    
        addr_struct = inet_aton(peer[0]) + struct.pack('! H', peer[1])
        addr_list.append(addr_struct)


    # 4 bytes action
    # 4 bytes trans_id
    # 4 bytes interval
    # 4 bytes leechers
    # 4 bytes seeders
    tracker_data = struct.pack('! i 4s i i i', 0, trans_id, settings["INTERVAL"], 1,1)

    addr_list_as_bytes = b''.join([addr for addr in addr_list])

    return tracker_data + addr_list_as_bytes


def random_bytes(length):
    # Generate a random string of lowercase letters
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length)).encode()

def validate_conn_request():
    # 4 bytes - action (0 for announce)
    # 4 bytes random trans_id
    # 8 bytes random conn_id 
    connection_id = random.randint(0, 2**32 - 1)

    # Create a validation message
    validation_msg = struct.pack("! q l l", connection_id, 0x0, 0x12345678)

    return validation_msg

async def on_regular_torrent_handshake(settings, local_conn, addr):
    print("handshake regular")
    to_send_back = validate_conn_request()
    local_conn.send(to_send_back, addr)
    await local_conn.drain()

    msg, addr = await asyncio.wait_for(local_conn.receive(), 1)

    resp = on_msg(settings, msg, addr)
    local_conn.send(resp, addr)
    await local_conn.drain()

def parse_torrentx_begin(msg):
    # conn id - 8 bytes
    # trans_id - 4 bytes
    # peer_id - 12 bytes
    # port - 2 bytes
    return struct.unpack("! q i 12s h", msg)    

def parse_torrentx_list(msg):
    #### FOR EACH TORRENT:
    # 20 bytes - info hash
    # 4 bytes - seeders
    # 4 bytes - leechers
    # 4 bytes - downloaded
    # 4 bytes - uploaded
    # 1 byte - announce type

    torrents = []


    struct_list = [msg[i:i+37] for i in range(0, len(msg), 37)]

    for strct in struct_list:
         torrents.append(struct.unpack("! 20s i i i i b", strct))

    return torrents

async def on_torrentx_handshake(settings, local_conn, addr):
    to_send_back = validate_conn_request()
    local_conn.send(to_send_back, addr)
    await local_conn.drain()

    msg, addr = await asyncio.wait_for(local_conn.receive(), 1)


    conn_id, trans_id, peer_id, port = parse_torrentx_begin(msg[:26])
    torrent_list = parse_torrentx_list(msg[26:])
    
    announce_resp = struct.pack("! q i i", conn_id, trans_id, settings["INTERVAL"]) 
    for info_hash, seeders, leechers, downloaded, uploaded, announce_type in torrent_list:
        t = None
        for torrent in lh.get_torrents():
            if torrent.info_hash == info_hash:
                t = torrent
                break

        if not t:
            announce_resp += struct.pack("! i i ", 0, 0)
            continue

        announce_log = AnnounceLog(datetime.datetime.now(), addr[0], port, announce_type, downloaded, uploaded, seeders, leechers)
        t.add_announcement(announce_log)
        announce_resp += struct.pack("! i i", len(t.get_peers()), 0) # need to fix it and find out how to put both seeders and leechers
        peers = t.get_peers()
        print(peers)
        for peer in peers:
            ip_bytes = struct.pack("! 4B", *[int(x) for x in peer[0].split(".")])
            announce_resp += ip_bytes + struct.pack("! h", peer[1])

    
    print(announce_resp)
    local_conn.send(announce_resp, addr)
    await local_conn.drain()

#####
    

async def main(settings):
    local_conn = await aioudp.open_local_endpoint(settings["IP"], settings["PORT"])
    print("started announce udp server")
    while True:
        try:
            msg, addr = await asyncio.wait_for(local_conn.receive(), 1)
        except TimeoutError:
            msg = None

        if msg:
            recv_prot_id = struct.unpack('! q', msg[:8])[0]
            if recv_prot_id == PROT_ID:
                await on_regular_torrent_handshake(settings, local_conn, addr)
            elif recv_prot_id == PROT_ID+1:
                print("torrentx handshake")
                await on_torrentx_handshake(settings, local_conn, addr)

        await asyncio.sleep(0.4)

def start(settings):
    asyncio.run(main(settings))
