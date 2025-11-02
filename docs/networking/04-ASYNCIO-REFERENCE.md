# Asyncio Networking Reference

Quick reference guide for asyncio networking concepts used in Cipherlink.

## Core Concepts

### What is Asyncio?

**Asyncio** = Asynchronous I/O
- Allows handling multiple network connections **concurrently**
- Uses **coroutines** (async functions) instead of threads
- More efficient than threads for I/O-bound operations

### Key Terms

- **Coroutine**: An async function that can pause/resume
- **Event Loop**: Manages which coroutines run when
- **await**: Pauses current coroutine, lets others run
- **StreamReader**: Reads data from socket (buffered)
- **StreamWriter**: Writes data to socket (buffered)

## Server Operations

### Create Server

```python
server = await asyncio.start_server(
    handle_client,    # Handler function (coroutine)
    '0.0.0.0',        # Bind address
    8888              # Bind port
)

# Start serving
async with server:
    await server.serve_forever()
```

### Handler Function Signature

```python
async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
):
    # reader: read data from client
    # writer: write data to client
    
    # Get client address
    addr = writer.get_extra_info('peername')
    print(f"Client from {addr}")
```

## Client Operations

### Connect to Server

```python
reader, writer = await asyncio.open_connection(
    '127.0.0.1',  # Server host
    8888          # Server port
)
```

## Reading Data

### Methods Overview

| Method | Description | Use Case |
|--------|-------------|----------|
| `read(n)` | Read up to n bytes | Don't know exact size |
| `readexactly(n)` | Read exactly n bytes | **Packet headers** |
| `readline()` | Read until newline | Text protocols |
| `readuntil(separator)` | Read until separator | Delimited data |

### Key Difference

```python
# ❌ WRONG for packet headers
header = await reader.read(9)  # Might get 5 bytes!

# ✅ CORRECT for packet headers
header = await reader.readexactly(9)  # Always gets 9 bytes
```

### Reading in Chunks

For variable-length data:

```python
# Step 1: Read header to get size
header = await reader.readexactly(9)

# Step 2: Parse size from header
version, nonce_size, data_size = struct.unpack('!BII', header)
total_size = nonce_size + data_size

# Step 3: Read exact amount
ciphertext = await reader.readexactly(total_size)
```

## Writing Data

### Basic Write

```python
# Write data
writer.write(b"Hello!")

# IMPORTANT: Wait for data to be sent!
await writer.drain()
```

### Why `drain()`?

TCP sockets are **buffered**:
- `write()` adds data to buffer (returns immediately)
- `drain()` waits until buffer is sent
- Without `drain()`, data might not be sent yet!

### Full Example

```python
# Pack packet
packet = Packet.pack(version, ciphertext)

# Send
writer.write(packet)
await writer.drain()  # Wait for send to complete
print("Data sent!")
```

## Connection Management

### Get Client Info

```python
# Get client address
addr = writer.get_extra_info('peername')
# Returns: ('127.0.0.1', 54321)

# Get server address
server_addr = writer.get_extra_info('sockname')
# Returns: ('0.0.0.0', 8888)
```

### Close Connection

```python
# Close connection
writer.close()

# Wait for connection to fully close
await writer.wait_closed()
```

### Proper Cleanup

Always use try/finally:

```python
try:
    # Do work
    data = await reader.read(1024)
    writer.write(response)
    await writer.drain()
except Exception as e:
    print(f"Error: {e}")
finally:
    # Always close
    writer.close()
    await writer.wait_closed()
```

## Error Handling

### Connection Errors

```python
try:
    data = await reader.readexactly(9)
except asyncio.IncompleteReadError:
    # Client disconnected before sending all data
    print("Client disconnected prematurely")
except ConnectionResetError:
    # Connection was reset
    print("Connection reset by peer")
except Exception as e:
    # Other errors
    print(f"Error: {e}")
```

### Timeout Handling

```python
# Read with timeout (5 seconds)
try:
    data = await asyncio.wait_for(
        reader.readexactly(9),
        timeout=5.0
    )
except asyncio.TimeoutError:
    print("Timeout: Client didn't send data in 5 seconds")
```

## Running Async Code

### Method 1: `asyncio.run()`

```python
async def main():
    # Your async code here
    await server.start()

if __name__ == '__main__':
    asyncio.run(main())
```

### Method 2: Event Loop (advanced)

```python
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
```

## Concurrent Connections

### How Multiple Clients Work

Each client gets its own coroutine:

```python
async def handle_client(reader, writer):
    # This runs for EACH client concurrently
    addr = writer.get_extra_info('peername')
    print(f"Handling {addr}")
    
    # All these clients run at the same time!
    # asyncio switches between them automatically

# Server handles all clients concurrently
server = await asyncio.start_server(handle_client, '0.0.0.0', 8888)
```

### Visual Example

```
Time →
Client 1: ───┐      ┌──────┐      ┌───
             │      │      │      │
Client 2:    │ ─────┘      │      │
             │             │      │
Client 3:    └─────────────┘ ─────┘
             All running concurrently!
```

## Common Patterns

### Pattern 1: Echo Server

```python
async def handle_client(reader, writer):
    try:
        # Read
        data = await reader.read(1024)
        
        # Echo back
        writer.write(data)
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()
```

### Pattern 2: Read Header Then Body

```python
# Read header (fixed size)
header = await reader.readexactly(9)

# Parse header
version, size1, size2 = struct.unpack('!BII', header)

# Read body (variable size)
total_size = size1 + size2
body = await reader.readexactly(total_size)
```

### Pattern 3: Send and Receive

```python
# Send packet
packet = create_packet(data)
writer.write(packet)
await writer.drain()

# Receive response
header = await reader.readexactly(9)
# ... parse and read rest ...
```

## Debugging Tips

### Enable Asyncio Debug Mode

```python
import asyncio

# Enable debug mode (shows detailed info)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # Windows only
asyncio.run(main(), debug=True)
```

### Add Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def handle_client(reader, writer):
    logger.debug(f"Client connected: {writer.get_extra_info('peername')}")
    # ...
```

### Check Connection State

```python
# Check if connection is closed
if writer.is_closing():
    print("Connection is closing")

# Check if write buffer is empty
if writer.get_write_buffer_size() == 0:
    print("All data sent")
```

## Performance Tips

### 1. Use `readexactly()` for Known Sizes

Faster and more reliable than `read()` when you know the size.

### 2. Batch Writes

```python
# Multiple small writes (slow)
writer.write(header)
await writer.drain()
writer.write(body)
await writer.drain()

# Single write (faster)
writer.write(header + body)
await writer.drain()
```

### 3. Limit Concurrent Connections

```python
# Limit to 100 concurrent connections
semaphore = asyncio.Semaphore(100)

async def handle_client(reader, writer):
    async with semaphore:
        # Handle client
        # ...
```

## FAQ

**Q: Why not use threads?**
A: Asyncio is more efficient for I/O-bound operations (networking). Threads are better for CPU-bound work.

**Q: What if I block in async code?**
A: Don't! Use `await` for I/O operations. Blocking code (like `time.sleep()`) blocks the entire event loop.

**Q: Can I mix async and sync code?**
A: Yes, but use `asyncio.run_in_executor()` to run blocking code:

```python
# Blocking code in executor
result = await asyncio.get_event_loop().run_in_executor(
    None,  # Use default executor
    blocking_function
)
```

**Q: How do I test async code?**
A: Use `pytest-asyncio`:

```python
import pytest

@pytest.mark.asyncio
async def test_client():
    client = ProxyClient('127.0.0.1', 8888)
    result = await client.forward(b"test")
    assert result == b"test"
```

## See Also

- [Python asyncio docs](https://docs.python.org/3/library/asyncio.html)
- [01-NETWORKING-FUNDAMENTALS.md](01-NETWORKING-FUNDAMENTALS.md)
- [02-ARCHITECTURE.md](02-ARCHITECTURE.md)
- [03-IMPLEMENTATION-GUIDE.md](03-IMPLEMENTATION-GUIDE.md)

