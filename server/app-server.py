import pandas as pd
import atexit
import signal
import sys

# Importing the relevant libraries
import websockets
import asyncio

from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent, GiftEvent, ShareEvent, LikeEvent, FollowEvent, ViewerCountUpdateEvent
 

# Server data
PORT = 7890
print("Server listening on Port " + str(PORT))

# A set of connected ws clients
connected = set()

# The main behavior function for this server
async def echo(websocket, path):
    print("A client just connected")
    # Store a copy of the connected client
    connected.add(websocket)
    # Handle incoming messages
    try:
        async for message in websocket:
            print("Received message from client: " + message)
            # Send a response to all connected clients except sender
            for conn in connected:
                if conn != websocket:
                    await conn.send("Someone said: " + message)
    # Handle disconnecting clients 
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
    finally:
        connected.remove(websocket)
    
async def publishMessage(message):
    print("Going to publish message: " + message)
    async for conn in connected:
            await conn.send(message)

listComment = [];

client: TikTokLiveClient = TikTokLiveClient(
    unique_id="duthien85", **(
        {
            "enable_extended_gift_info": True
        }
    )
)

@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Connect to Room Id:", client.room_id)

@client.on("comment")
async def on_connect(event: CommentEvent):
    print(f"{event.user.uniqueId} -> {event.comment}")
    listComment.append({'username': event.user.uniqueId, 'Comment': event.comment})
    print('----------------------')
    publishMessage(f"{event.user.uniqueId} -> {event.comment}")
    # df = pd.DataFrame({'Username':[event.user.uniqueId],'Comment':[event.comment]})
    # df.to_excel('tikTokLiveData.xlsx', header=None, index=True, encoding='utf-8')

@client.on("gift")
async def on_gift(event: GiftEvent):
    print(f"{event.user.uniqueId} sent a gift")
    # print(f"{event.user.uniqueId} sent a {event.gift.gift_id}!")
    # for giftInfo in client.available_gifts:
    #     if giftInfo["id"] == event.gift.gift_id:
    #         print(f"Name: {giftInfo['name']} Image: {giftInfo['image']['url_list'][0]} Diamond Amount: {giftInfo['diamond_count']}")

@client.on("like")
async def on_like(event: LikeEvent):
    print(f"{event.user.uniqueId} has liked the stream {event.likeCount} time, there is now {event.totalLikeCount} total likes!")

@client.on("follow")
async def on_follow(event: FollowEvent):
    print(f"{event.user.uniqueId} followed the streamer")

@client.on("share")
async def on_share(event: ShareEvent):
    print(f"{event.user.uniqueId} shared the stream!")

@client.on("viewer_count_update")
async def on_connect(event: ViewerCountUpdateEvent):
    print("Received a new vewer count:", event.viewerCount)

def exit_handler():
    print('App is ending, going to save excel:' + listComment)

def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Going to save excel: ')
    df = pd.DataFrame(listComment)
    df.to_excel('tikTokLiveData.xlsx', header=None, index=True, encoding='utf-8')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


# Start the server ws
start_server = websockets.serve(echo, "localhost", PORT)
# if __name__ == '__main__':
    # Run the client and block the main thread
    # Await client.start() to run non-blocking

    
asyncio.get_event_loop().run_until_complete(start_server)

client.run()

asyncio.get_event_loop().run_forever()

# if __name__ == '__main__':
#     # Run the client and block the main thread
#     # Await client.start() to run non-blocking

#     client.run()
