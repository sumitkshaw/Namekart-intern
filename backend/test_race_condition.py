import asyncio
import aiohttp
import json

async def test_concurrent_updates():
    """Test race condition protection"""
    
    # First, create a note
    async with aiohttp.ClientSession() as session:
        # Create note
        async with session.post('http://localhost:8000/api/notes', 
                              json={'content': 'Original content'}) as resp:
            note = await resp.json()
            note_id = note['id']
            version = note['version']
            print(f"Created note {note_id} with version {version}")
        
        # Simulate two concurrent updates
        async def update_note(session, suffix, delay=0):
            if delay:
                await asyncio.sleep(delay)
            try:
                async with session.put(f'http://localhost:8000/api/notes/{note_id}',
                                     json={
                                         'content': f'Updated content {suffix}',
                                         'version': version  # Both use same version
                                     }) as resp:
                    result = await resp.json()
                    print(f"Update {suffix}: SUCCESS - {result}")
                    return resp.status
            except Exception as e:
                print(f"Update {suffix}: ERROR - {e}")
        
        # Start both updates simultaneously
        results = await asyncio.gather(
            update_note(session, "A"),
            update_note(session, "B", 0.1),  # Slight delay
            return_exceptions=True
        )
        
        print(f"Results: {results}")

if __name__ == "__main__":
    print("Testing race condition protection...")
    asyncio.run(test_concurrent_updates())