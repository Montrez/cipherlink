# Step-by-Step Implementation Guide

This guide walks through implementing the client/server connection step by step.

## Prerequisites

Before starting, make sure you:
- ✅ Understand [01-NETWORKING-FUNDAMENTALS.md](01-NETWORKING-FUNDAMENTALS.md)
- ✅ Understand [02-ARCHITECTURE.md](02-ARCHITECTURE.md)
- ✅ Have read `common/crypto.py` and `common/protocol.py`
- ✅ Have a shared encryption key generated (`python scripts/genkeys.py`)

## Part 1: Server Implementation

### Step 1: Basic Server Structure

Start with the skeleton in `server/proxy.py`:

```python
"""Server-side proxy implementation for Phase 1."""
import asyncio
from pathlib import Path
from common.crypto import CryptoBox
from common.protocol import Packet, PROTOCOL_VERSION, HEADER_SIZE

class ProxyServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 8888, key_path: str = 'keys/shared_key.key'):
        self.host = host
        self.port = port
        self.key_path = key_path
        self.crypto_box = None  # Will be set in start()
    
    async def start(self):
        """Start the proxy server."""
        # TODO: Implement server startup
        pass
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming client connection."""
        # TODO: Implement client handling logic
        pass
```

### Step 2: Load Encryption Key

First, we need to load the shared encryption key:

```python
async def start(self):
    """Start the proxy server."""
    # Load encryption key
    key_file = Path(self.key_path)
    if not key_file.exists():
        raise FileNotFoundError(f"Key file not found: {self.key_path}")
    
    # Read the 32-byte key
    key = key_file.read_bytes()
    
    # Create CryptoBox for encryption/decryption
    self.crypto_box = CryptoBox(key)
    
    print(f"Server key loaded from {self.key_path}")
```

**Key Points:**
- Keys are stored as raw bytes (32 bytes for PyNaCl)
- CryptoBox needs this key to encrypt/decrypt
- Server and client must use the SAME key

### Step 3: Start Async Server

Now start the asyncio server:

```python
async def start(self):
    """Start the proxy server."""
    # Load encryption key (from Step 2)
    key_file = Path(self.key_path)
    if not key_file.exists():
        raise FileNotFoundError(f"Key file not found: {self.key_path}")
    
    key = key_file.read_bytes()
    self.crypto_box = CryptoBox(key)
    
    print(f"Server key loaded from {self.key_path}")
    
    # Create async server
    server = await asyncio.start_server(
        self.handle_client,  # Function to call for each client
        self.host,           # Bind address
        self.port            # Bind port
    )
    
    # Get server address
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr[0]}:{addr[1]}")
    
    # Start serving forever
    async with server:
        await server.serve_forever()
```

**Key Points:**
- `asyncio.start_server()` creates the server
- `self.handle_client` is called for each new connection
- `serve_forever()` keeps the server running

### Step 4: Handle Client Connection - Read Header

Implement `handle_client()` to read the packet header:

```python
async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle incoming client connection."""
    try:
        # Get client address
        addr = writer.get_extra_info('peername')
        print(f"Client connected from {addr}")
        
        # Step 1: Read packet header (exactly 9 bytes)
        header = await reader.readexactly(HEADER_SIZE)
        print(f"Received header: {len(header)} bytes")
        
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        # Always close the connection
        writer.close()
        await writer.wait_closed()
```

**Key Points:**
- `readexactly(9)` reads exactly 9 bytes (waits until all arrive)
- Use try/except to handle errors gracefully
- Always close connection in `finally` block

### Step 5: Parse Header and Read Ciphertext

Extend `handle_client()` to parse header and read the rest:

```python
async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle incoming client connection."""
    try:
        addr = writer.get_extra_info('peername')
        print(f"Client connected from {addr}")
        
        # Step 1: Read header
        header = await reader.readexactly(HEADER_SIZE)
        
        # Step 2: Parse header to get sizes
        import struct
        version, nonce_size, data_size = struct.unpack('!BII', header)
        print(f"Packet: version={version}, nonce_size={nonce_size}, data_size={data_size}")
        
        # Step 3: Read ciphertext (nonce + encrypted data)
        total_ciphertext_size = nonce_size + data_size
        ciphertext = await reader.readexactly(total_ciphertext_size)
        print(f"Read ciphertext: {len(ciphertext)} bytes")
        
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
```

**Key Points:**
- `struct.unpack('!BII', header)` unpacks:
  - `!` = network byte order (big-endian)
  - `B` = unsigned char (1 byte) for version
  - `I` = unsigned int (4 bytes) for nonce_size
  - `I` = unsigned int (4 bytes) for data_size
- Total ciphertext = nonce_size + data_size

### Step 6: Unpack and Decrypt

Add unpacking and decryption:

```python
async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle incoming client connection."""
    try:
        addr = writer.get_extra_info('peername')
        print(f"Client connected from {addr}")
        
        # Step 1: Read header
        header = await reader.readexactly(HEADER_SIZE)
        
        # Step 2: Parse header
        import struct
        version, nonce_size, data_size = struct.unpack('!BII', header)
        
        # Step 3: Read ciphertext
        total_ciphertext_size = nonce_size + data_size
        ciphertext = await reader.readexactly(total_ciphertext_size)
        
        # Step 4: Unpack packet
        full_packet = header + ciphertext
        packet_info = Packet.unpack(full_packet)
        
        if packet_info is None:
            print("Invalid packet format")
            return
        
        version_received, ciphertext_only = packet_info
        print(f"Unpacked packet: version={version_received}")
        
        # Step 5: Decrypt
        plaintext = self.crypto_box.decrypt(ciphertext_only)
        print(f"Decrypted: {plaintext.decode('utf-8', errors='ignore')}")
        
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
```

**Key Points:**
- `Packet.unpack()` validates and extracts ciphertext
- Returns `None` if packet is invalid
- `crypto_box.decrypt()` decrypts the ciphertext

### Step 7: Echo Response

Add code to echo back the message:

```python
async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Handle incoming client connection."""
    try:
        addr = writer.get_extra_info('peername')
        print(f"Client connected from {addr}")
        
        # ... (previous steps) ...
        
        # Step 5: Decrypt
        plaintext = self.crypto_box.decrypt(ciphertext_only)
        print(f"Decrypted: {plaintext.decode('utf-8', errors='ignore')}")
        
        # Step 6: Echo back (for testing)
        response_plaintext = plaintext  # Just echo
        
        # Step 7: Encrypt response
        response_ciphertext = self.crypto_box.encrypt(response_plaintext)
        
        # Step 8: Pack response
        response_packet = Packet.pack(PROTOCOL_VERSION, response_ciphertext)
        
        # Step 9: Send response
        writer.write(response_packet)
        await writer.drain()  # Wait for data to be sent
        print(f"Sent response: {len(response_packet)} bytes")
        
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
```

### Step 8: Add Main Entry Point

Add a main function to run the server:

```python
async def main():
    """Run the proxy server."""
    server = ProxyServer(host='0.0.0.0', port=8888)
    await server.start()

if __name__ == '__main__':
    asyncio.run(main())
```

## Part 2: Client Implementation

### Step 1: Basic Client Structure

Start with the skeleton in `client/proxy.py`:

```python
"""Client-side proxy implementation for Phase 1."""
import asyncio
from pathlib import Path
from common.crypto import CryptoBox
from common.protocol import Packet, PROTOCOL_VERSION, HEADER_SIZE

class ProxyClient:
    def __init__(self, server_host: str, server_port: int, key_path: str = 'keys/shared_key.key'):
        self.server_host = server_host
        self.server_port = server_port
        self.key_path = key_path
        self.crypto_box = None  # Will be set in connect()
    
    async def connect(self):
        """Establish connection to proxy server."""
        # TODO: Implement connection logic
        pass
    
    async def forward(self, data: bytes):
        """Forward encrypted data through tunnel."""
        # TODO: Implement forwarding logic
        pass
```

### Step 2: Connect to Server

Implement the `connect()` method:

```python
async def connect(self):
    """Establish connection to proxy server."""
    # Load encryption key
    key_file = Path(self.key_path)
    if not key_file.exists():
        raise FileNotFoundError(f"Key file not found: {self.key_path}")
    
    key = key_file.read_bytes()
    self.crypto_box = CryptoBox(key)
    
    print(f"Client key loaded from {self.key_path}")
    
    # Connect to server
    reader, writer = await asyncio.open_connection(
        self.server_host,
        self.server_port
    )
    
    print(f"Connected to {self.server_host}:{self.server_port}")
    
    return reader, writer
```

### Step 3: Send Data

Implement the `forward()` method:

```python
async def forward(self, data: bytes):
    """Forward encrypted data through tunnel."""
    # Connect to server
    reader, writer = await self.connect()
    
    try:
        # Step 1: Encrypt data
        ciphertext = self.crypto_box.encrypt(data)
        print(f"Encrypted {len(data)} bytes → {len(ciphertext)} bytes")
        
        # Step 2: Pack into packet
        packet = Packet.pack(PROTOCOL_VERSION, ciphertext)
        print(f"Packed packet: {len(packet)} bytes")
        
        # Step 3: Send packet
        writer.write(packet)
        await writer.drain()
        print("Packet sent")
        
        # Step 4: Read response header
        header = await reader.readexactly(HEADER_SIZE)
        
        # Step 5: Parse header
        import struct
        version, nonce_size, data_size = struct.unpack('!BII', header)
        
        # Step 6: Read ciphertext
        total_size = nonce_size + data_size
        ciphertext = await reader.readexactly(total_size)
        
        # Step 7: Unpack response
        full_packet = header + ciphertext
        packet_info = Packet.unpack(full_packet)
        
        if packet_info is None:
            raise ValueError("Invalid response packet")
        
        version, response_ciphertext = packet_info
        
        # Step 8: Decrypt response
        plaintext = self.crypto_box.decrypt(response_ciphertext)
        print(f"Received response: {plaintext.decode('utf-8', errors='ignore')}")
        
        return plaintext
        
    finally:
        # Always close connection
        writer.close()
        await writer.wait_closed()
```

### Step 4: Add Main Entry Point

Add a test main function:

```python
async def main():
    """Test the client."""
    client = ProxyClient('127.0.0.1', 8888)
    
    # Send a test message
    response = await client.forward(b"Hello, Server!")
    print(f"Final response: {response}")

if __name__ == '__main__':
    asyncio.run(main())
```

## Testing the Implementation

### Step 1: Start Server

```bash
# Terminal 1
cd /path/to/cipherlink
python server/proxy.py
```

Expected output:
```
Server key loaded from keys/shared_key.key
Server listening on 0.0.0.0:8888
```

### Step 2: Run Client

```bash
# Terminal 2
cd /path/to/cipherlink
python client/proxy.py
```

Expected output:
```
Client key loaded from keys/shared_key.key
Connected to 127.0.0.1:8888
Encrypted 14 bytes → 46 bytes
Packed packet: 55 bytes
Packet sent
Received response: Hello, Server!
Final response: b'Hello, Server!'
```

Server should show:
```
Client connected from ('127.0.0.1', 54321)
Packet: version=1, nonce_size=24, data_size=22
Read ciphertext: 46 bytes
Unpacked packet: version=1
Decrypted: Hello, Server!
Sent response: 55 bytes
```

## Common Issues and Solutions

### Issue 1: "Key file not found"
**Solution:** Run `python scripts/genkeys.py` first

### Issue 2: "Connection refused"
**Solution:** Make sure server is running before starting client

### Issue 3: "readexactly() failed"
**Solution:** Client might have disconnected. Add better error handling.

### Issue 4: "decryption failed"
**Solution:** Make sure client and server use the SAME key file

## Next Steps

1. ✅ Basic client/server connection working
2. ⏭️ Add timeout handling (Phase 1 task)
3. ⏭️ Add support for multiple clients (Phase 1 task)
4. ⏭️ Implement SOCKS5 protocol (Phase 1 task)

## Reference

- See [04-ASYNCIO-REFERENCE.md](04-ASYNCIO-REFERENCE.md) for asyncio details
- See `common/crypto.py` for encryption details
- See `common/protocol.py` for packet format details

