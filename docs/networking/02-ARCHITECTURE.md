# Cipherlink Architecture: Client-Server Connection

This document explains the architecture of our encrypted proxy connection.

## High-Level Overview

```
┌─────────────┐                    ┌─────────────┐
│   Client    │                    │   Server   │
│ Application │                    │            │
└──────┬──────┘                    └──────┬─────┘
       │                                  │
       │ 1. Establishes TCP connection   │
       ├─────────────────────────────────>│
       │                                  │
       │ 2. Sends encrypted packet        │
       │    (plaintext → encrypt → pack)  │
       ├─────────────────────────────────>│
       │                                  │
       │                                  │ 3. Receives packet
       │                                  │    (unpack → decrypt)
       │                                  │
       │ 4. Receives response             │
       │    (unpack → decrypt)            │<─────────────────────┤
       │                                  │
       │ 5. Close connection              │
       ├─────────────────────────────────>│
       │                                  │
```

## Component Breakdown

### 1. Client Components (`client/proxy.py`)

```
ProxyClient
├── __init__(server_host, server_port)
│   └── Stores server address info
│
├── connect()
│   ├── asyncio.open_connection()
│   ├── Load encryption key
│   ├── Create CryptoBox
│   └── Return reader, writer
│
└── forward(data: bytes)
    ├── Encrypt data (CryptoBox)
    ├── Pack into packet (Packet.pack)
    ├── Send packet (writer.write)
    ├── Wait for send (writer.drain)
    ├── Read response (reader.readexactly)
    ├── Unpack response (Packet.unpack)
    ├── Decrypt response (CryptoBox)
    └── Return plaintext
```

### 2. Server Components (`server/proxy.py`)

```
ProxyServer
├── __init__(host, port)
│   └── Stores bind address
│
├── start()
│   ├── Load encryption key
│   ├── Create CryptoBox
│   ├── asyncio.start_server()
│   ├── Register handle_client
│   └── server.serve_forever()
│
└── handle_client(reader, writer)
    ├── Read packet header (9 bytes)
    ├── Unpack header (get sizes)
    ├── Read ciphertext
    ├── Unpack full packet
    ├── Decrypt data
    ├── Process plaintext (echo for now)
    ├── Encrypt response
    ├── Pack response
    ├── Send response
    └── Close connection
```

### 3. Shared Components (`common/`)

#### CryptoBox (`common/crypto.py`)
```
CryptoBox
├── __init__(key: bytes)
│   └── Creates SecretBox with 32-byte key
│
├── encrypt(plaintext: bytes) -> bytes
│   ├── Generate random nonce (24 bytes)
│   ├── Encrypt plaintext with nonce
│   └── Return: nonce + ciphertext
│
└── decrypt(ciphertext: bytes) -> bytes
    ├── Extract nonce (first 24 bytes)
    ├── Decrypt rest with nonce
    └── Return plaintext
```

#### Packet (`common/protocol.py`)
```
Packet
├── pack(version: int, ciphertext: bytes) -> bytes
│   ├── Calculate sizes
│   ├── Create header: version (1) + nonce_size (4) + data_size (4)
│   └── Return: header + ciphertext
│
└── unpack(data: bytes) -> Tuple[int, bytes] | None
    ├── Validate header size
    ├── Parse header (version, nonce_size, data_size)
    ├── Extract ciphertext
    └── Return: (version, ciphertext)
```

## Data Flow: Detailed Example

Let's trace a complete request:

### Step 1: Client Initialization

```python
# Client creates ProxyClient
client = ProxyClient('127.0.0.1', 8888)
```

### Step 2: Client Connects

```python
# Client calls connect()
reader, writer = await client.connect()

# What happens:
# 1. Opens TCP connection to 127.0.0.1:8888
# 2. Creates CryptoBox with shared key
# 3. Returns (reader, writer) for communication
```

**Network Layer:**
```
Client                                    Server
  │                                         │
  │  SYN (synchronize)                     │
  │ ──────────────────────────────────────> │
  │                                         │
  │  SYN-ACK                               │
  │ <────────────────────────────────────── │
  │                                         │
  │  ACK (acknowledge)                     │
  │ ──────────────────────────────────────> │
  │                                         │
  │ Connection Established! ✅             │
```

### Step 3: Client Sends Data

```python
# Application wants to send "Hello!"
plaintext = b"Hello!"

# Client encrypts and sends
response = await client.forward(plaintext)
```

**Inside `forward()`:**

```python
# 1. Encrypt plaintext
ciphertext = crypto_box.encrypt(b"Hello!")
# Result: nonce (24 bytes) + encrypted "Hello!" (variable)

# 2. Pack into protocol format
packet = Packet.pack(PROTOCOL_VERSION, ciphertext)
# Result: header (9 bytes) + ciphertext

# 3. Send over TCP
writer.write(packet)
await writer.drain()

# 4. Read response header
header = await reader.readexactly(9)

# 5. Unpack header
version, nonce_size, data_size = struct.unpack('!BII', header)
total_size = nonce_size + data_size

# 6. Read ciphertext
ciphertext = await reader.readexactly(total_size)

# 7. Unpack full packet
version, ciphertext = Packet.unpack(header + ciphertext)

# 8. Decrypt
plaintext = crypto_box.decrypt(ciphertext)

# 9. Return plaintext
return plaintext
```

**Network Layer:**
```
Client                                    Server
  │                                         │
  │ [Header: 9 bytes]                     │
  │ [Ciphertext: variable]                 │
  │ ──────────────────────────────────────> │
  │                                         │
  │                                         │ Receive header
  │                                         │ Parse sizes
  │                                         │ Read ciphertext
  │                                         │ Unpack packet
  │                                         │ Decrypt: "Hello!"
  │                                         │ Process...
  │                                         │
  │ [Response Header: 9 bytes]             │
  │ [Response Ciphertext: variable]        │
  │ <────────────────────────────────────── │
  │                                         │
  │ Receive response                       │
  │ Unpack & decrypt                       │
```

### Step 4: Server Handles Request

```python
# Server receives connection
async def handle_client(reader, writer):
    # 1. Read header
    header = await reader.readexactly(9)
    
    # 2. Parse header
    version, nonce_size, data_size = struct.unpack('!BII', header)
    
    # 3. Read ciphertext
    ciphertext = await reader.readexactly(nonce_size + data_size)
    
    # 4. Unpack packet
    version, ciphertext = Packet.unpack(header + ciphertext)
    
    # 5. Decrypt
    plaintext = crypto_box.decrypt(ciphertext)
    # plaintext = b"Hello!"
    
    # 6. Process (for now, just echo back)
    response = plaintext  # b"Hello!"
    
    # 7. Encrypt response
    response_ciphertext = crypto_box.encrypt(response)
    
    # 8. Pack response
    response_packet = Packet.pack(PROTOCOL_VERSION, response_ciphertext)
    
    # 9. Send response
    writer.write(response_packet)
    await writer.drain()
    
    # 10. Close connection
    writer.close()
    await writer.wait_closed()
```

### Step 5: Connection Closed

```python
# Client closes
writer.close()
await writer.wait_closed()
```

**Network Layer:**
```
Client                                    Server
  │                                         │
  │  FIN (finish)                          │
  │ ──────────────────────────────────────> │
  │                                         │
  │  FIN-ACK                               │
  │ <────────────────────────────────────── │
  │                                         │
  │  ACK                                   │
  │ ──────────────────────────────────────> │
  │                                         │
  │ Connection Closed ✅                   │
```

## Memory Layout: Packet Structure

Let's visualize a complete packet in memory:

```
Byte Offset:  0    1    2    3    4    5    6    7    8    9    ...
              ┌────┐┌───────────────────┐┌───────────────────┐
              │Ver ││  Nonce Size (4B)  ││  Data Size (4B)    │
              └────┘└───────────────────┘└───────────────────┘
              ┌─────────────────────────────────────────────────┐
              │            Nonce (24 bytes)                     │
              │  [Random bytes for encryption security]          │
              └─────────────────────────────────────────────────┘
              ┌─────────────────────────────────────────────────┐
              │         Encrypted Data (variable)               │
              │  [Original plaintext encrypted with nonce]      │
              └─────────────────────────────────────────────────┘

Example: Sending "Hello!" (6 bytes)
- Header: 9 bytes
  - Version: 0x01 (1 byte)
  - Nonce Size: 0x00000018 (24 bytes, big-endian)
  - Data Size: 0x00000020 (32 bytes encrypted "Hello!", big-endian)
- Nonce: 24 bytes (random)
- Ciphertext: 32 bytes (encrypted "Hello!")
Total: 9 + 24 + 32 = 65 bytes
```

## Error Handling Flow

```
Client sends packet
       │
       ▼
   ┌─────────┐
   │ Server  │
   │ receives│
   └────┬────┘
        │
        ▼
   ┌─────────────┐
   │ Valid       │
   │ packet?     │
   └─┬──────┬────┘
     │      │
   Yes      No
     │      │
     │      ▼
     │   ┌──────────────┐
     │   │ Send error    │
     │   │ Close conn    │
     │   └──────────────┘
     │
     ▼
   ┌─────────────┐
   │ Decrypt     │
   │ successful?│
   └─┬──────┬────┘
     │      │
   Yes      No
     │      │
     │      ▼
     │   ┌──────────────┐
     │   │ Send error    │
     │   │ Close conn    │
     │   └──────────────┘
     │
     ▼
   ┌─────────────┐
   │ Process     │
   │ data        │
   └─────────────┘
```

## Concurrency Model

### Server Handles Multiple Clients

```
Time →
      │
Client 1│───┐
      │    │
Client 2│   │   ───┐
      │    │      │
Client 3│   │      │   ───┐
      │    │      │      │
      │    │      │      │ All handled concurrently!
      │    │      │      │
      └────┴──────┴──────┴
      handle handle handle
      client client client
      1      2      3
```

Each client gets its own `handle_client()` coroutine running concurrently.

### Why Asyncio?

Without asyncio (blocking):
```
Client 1: ────────────┐ (blocks during read)
                       │
Client 2:              └───┐ (waits for client 1)
                            │
Client 3:                   └───┐ (waits for client 2)
```

With asyncio:
```
Client 1: ───────┐      ┌───────┐
                 │      │       │
Client 2: ───────┼──────┘       │
                 │              │
Client 3: ───────┴──────────────┘
          (all handled concurrently)
```

## Next Steps

Now that you understand the architecture:
1. See [03-IMPLEMENTATION-GUIDE.md](03-IMPLEMENTATION-GUIDE.md) for step-by-step code
2. See [04-ASYNCIO-REFERENCE.md](04-ASYNCIO-REFERENCE.md) for asyncio details

