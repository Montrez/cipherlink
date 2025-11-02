# Networking Fundamentals for Cipherlink

This document breaks down the networking concepts you'll need to implement the client/server connection in Cipherlink.

## Table of Contents
1. [TCP Sockets Basics](#tcp-sockets-basics)
2. [Client-Server Model](#client-server-model)
3. [Asyncio Networking](#asyncio-networking)
4. [Byte Streams and Framing](#byte-streams-and-framing)
5. [Our Encrypted Tunnel](#our-encrypted-tunnel)

---

## TCP Sockets Basics

### What is a Socket?

Think of a socket like a **phone line** between two computers:
- One computer **listens** for calls (server)
- Another computer **dials** the number (client)
- Once connected, they can send **data** back and forth
- When done, they **hang up** (close connection)

### TCP vs UDP

**TCP (Transmission Control Protocol)** - What we're using
- ✅ **Reliable**: Data is guaranteed to arrive
- ✅ **Ordered**: Data arrives in the order it was sent
- ✅ **Connection-oriented**: Requires a "handshake" before sending data
- ✅ **Stream-based**: Data flows like water through a pipe

**UDP (User Datagram Protocol)** - Not using this
- ❌ **Unreliable**: Data might be lost
- ❌ **Unordered**: Data might arrive out of order
- ❌ **Connectionless**: No handshake needed
- ❌ **Packet-based**: Data sent in discrete chunks

### Why TCP for Cipherlink?

We need **reliability** for our encrypted tunnel. If data is lost, the encryption layer won't work correctly.

---

## Client-Server Model

### The Restaurant Analogy

Think of our proxy like a restaurant:

**Server** = The Restaurant
- Opens at a specific **address** (IP: `127.0.0.1`) and **table number** (port: `8888`)
- **Waits** for customers (clients) to arrive
- When a customer arrives, assigns them a **waiter** (connection handler)
- Can handle **multiple customers** at once (multiple clients)

**Client** = The Customer
- **Goes to** the restaurant address (`127.0.0.1:8888`)
- **Sits down** (establishes connection)
- **Orders food** (sends data)
- **Receives food** (receives data)
- **Pays and leaves** (closes connection)

### In Code Terms

**Server Side:**
```python
# 1. Create a socket and bind to address:port
socket.bind(('0.0.0.0', 8888))

# 2. Start listening for connections
socket.listen()

# 3. Accept incoming connections (blocks until client connects)
client_socket, address = socket.accept()

# 4. Send/receive data
data = client_socket.recv(1024)  # Receive up to 1024 bytes
client_socket.send(b"Hello!")     # Send data back

# 5. Close connection
client_socket.close()
```

**Client Side:**
```python
# 1. Create a socket
socket = socket.socket()

# 2. Connect to server
socket.connect(('127.0.0.1', 8888))

# 3. Send/receive data
socket.send(b"Hello!")
data = socket.recv(1024)

# 4. Close connection
socket.close()
```

---

## Asyncio Networking

### The Problem with Traditional Sockets

**Blocking I/O** (traditional sockets):
```python
# This BLOCKS - program freezes until data arrives
data = socket.recv(1024)  # ⏸️ WAITING...
print(data)  # Only executes after data arrives
```

If we have 10 clients, we'd need 10 threads (complicated!) or accept clients one at a time (slow!).

### The Solution: Async I/O

**Asyncio** lets us handle **multiple connections concurrently** without threads:

```python
# This doesn't block! We can handle other connections while waiting
data = await reader.read(1024)  # ⏳ YIELD - let other tasks run
print(data)  # Executes when data arrives
```

### Key Asyncio Concepts

#### 1. **Coroutines (async functions)**
```python
async def handle_client(reader, writer):
    """This is a coroutine - can pause and resume"""
    data = await reader.read(1024)  # Pause here, resume when data arrives
    writer.write(data)              # Send data back
    await writer.drain()            # Wait for data to be sent
```

#### 2. **Event Loop**
- Like a **traffic controller** for async operations
- Manages which coroutines run when
- When one task waits (`await`), it switches to another task

#### 3. **Streams (reader/writer)**
- **StreamReader**: Read data from the socket
- **StreamWriter**: Write data to the socket
- These are **buffered** - data might come in chunks

#### 4. **Server Example**
```python
async def start_server():
    """Start async server"""
    # Create server, bind to address
    server = await asyncio.start_server(
        handle_client,    # Function to call for each client
        '127.0.0.1',      # Host
        8888              # Port
    )
    
    # Start serving forever
    async with server:
        await server.serve_forever()

# Run the server
asyncio.run(start_server())
```

#### 5. **Client Example**
```python
async def connect_to_server():
    """Connect as client"""
    # Connect to server
    reader, writer = await asyncio.open_connection(
        '127.0.0.1',  # Host
        8888          # Port
    )
    
    # Send data
    writer.write(b"Hello!")
    await writer.drain()  # Wait for data to be sent
    
    # Receive data
    data = await reader.read(1024)
    print(f"Received: {data}")
    
    # Close connection
    writer.close()
    await writer.wait_closed()

# Run the client
asyncio.run(connect_to_server())
```

---

## Byte Streams and Framing

### The Problem: TCP is a Stream

TCP doesn't preserve message boundaries:
- Send: `"Hello"` + `"World"`
- Receive: Might get `"HelloWorld"` all at once, or `"Hel"` then `"loWorld"`, etc.

### Solution: Framing (Packet Headers)

We need to tell the receiver: **"How much data is coming?"**

This is why we have the `Packet` class in `common/protocol.py`:

```
Packet Structure:
┌─────────────────────────────────────────────────┐
│ Header (9 bytes)                                 │
├──────────┬───────────┬───────────────────────────┤
│ Version  │ Nonce     │ Data Size                │
│ (1 byte) │ Size      │ (4 bytes)                │
│          │ (4 bytes) │                          │
└──────────┴───────────┴───────────────────────────┘
│ Ciphertext (variable length)                    │
│ - Nonce (24 bytes)                              │
│ - Encrypted data (rest)                          │
└─────────────────────────────────────────────────┘
```

### Reading Packets

Since TCP is a stream, we read in chunks:

1. **Read header** (9 bytes) - this tells us how much data is coming
2. **Read the rest** (nonce + encrypted data) based on size from header
3. **Unpack** the packet to get version and ciphertext
4. **Decrypt** the ciphertext

```python
# Step 1: Read header (9 bytes)
header = await reader.readexactly(9)  # Exactly 9 bytes!

# Step 2: Unpack header to get data size
version, nonce_size, data_size = struct.unpack('!BII', header)
total_ciphertext_size = nonce_size + data_size

# Step 3: Read ciphertext
ciphertext = await reader.readexactly(total_ciphertext_size)

# Step 4: Unpack full packet
packet_data = Packet.unpack(header + ciphertext)
version, ciphertext = packet_data

# Step 5: Decrypt
plaintext = crypto_box.decrypt(ciphertext)
```

**Key Method: `readexactly()`**
- `reader.read(1024)` - Read up to 1024 bytes (might return less!)
- `reader.readexactly(1024)` - Read exactly 1024 bytes (waits until all 1024 bytes arrive)

---

## Our Encrypted Tunnel

### How It Works

```
Client                                    Server
  │                                         │
  │ 1. Connect to server                   │
  │ ────────────────────────────────>       │
  │                                         │
  │ 2. Send encrypted packet                │
  │    - Encrypt plaintext data             │
  │    - Pack into packet format            │
  │ ────────────────────────────────>       │
  │                                         │
  │                                         │ 3. Receive packet
  │                                         │    - Unpack header
  │                                         │    - Read ciphertext
  │                                         │    - Decrypt data
  │                                         │
  │ 4. Receive response                     │
  │ <────────────────────────────────       │
  │                                         │
```

### Data Flow

```
Application Data (Plaintext)
         │
         ▼
   ┌─────────────┐
   │  Encrypt    │  ← Uses CryptoBox with shared key
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │    Pack     │  ← Adds header (version, sizes)
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │ Send over   │  ← TCP socket
   │   socket    │
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │  Receive    │  ← TCP socket
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │   Unpack    │  ← Reads header, gets sizes
   └─────────────┘
         │
         ▼
   ┌─────────────┐
   │  Decrypt    │  ← Uses CryptoBox with shared key
   └─────────────┘
         │
         ▼
Application Data (Plaintext)
```

### Security Layer

Every packet is encrypted:
1. **Plaintext** (original data) → **Encrypt** → **Ciphertext**
2. Add **nonce** (number used once) for security
3. Wrap in **packet header** with sizes
4. Send over network
5. Receiver: **Unpack** → **Decrypt** → **Plaintext**

The nonce ensures that even if we send the same data twice, the ciphertext is different!

---

## Common Pitfalls

### 1. **Assuming read() gets all data**
```python
# ❌ WRONG - might not get all 1024 bytes!
data = await reader.read(1024)

# ✅ CORRECT - waits for exactly 9 bytes
header = await reader.readexactly(9)
```

### 2. **Forgetting to drain writer**
```python
# ❌ WRONG - data might not be sent yet!
writer.write(b"Hello")

# ✅ CORRECT - wait for data to be sent
writer.write(b"Hello")
await writer.drain()
```

### 3. **Not closing connections**
```python
# ✅ ALWAYS close when done
writer.close()
await writer.wait_closed()
```

### 4. **Not handling exceptions**
```python
# ✅ Wrap in try/except
try:
    data = await reader.read(1024)
except ConnectionError:
    print("Client disconnected!")
    break
```

---

## Next Steps

Now that you understand the networking concepts, check out:
- [02-ARCHITECTURE.md](02-ARCHITECTURE.md) - Overall architecture
- [03-IMPLEMENTATION-GUIDE.md](03-IMPLEMENTATION-GUIDE.md) - Step-by-step implementation
- [04-ASYNCIO-REFERENCE.md](04-ASYNCIO-REFERENCE.md) - Asyncio cheat sheet

