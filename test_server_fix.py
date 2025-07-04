#!/usr/bin/env python3
"""
Test script to check if the deployed server has the bug fix
"""

import aiohttp
import asyncio
import json

async def test_server():
    try:
        url = 'https://notion-mcp-server-5s5v.onrender.com/'
        
        print("🧪 Testing deployed server...")
        print("=" * 50)
        
        # Test health check first
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print('✅ Server is running:', data.get('status'))
                    
                    # Test page creation
                    print("\n📄 Testing page creation...")
                    request_data = {
                        'jsonrpc': '2.0',
                        'method': 'tools/call',
                        'params': {
                            'name': 'create_notion_page',
                            'arguments': {
                                'title': 'Test Bug Fix Page',
                                'content': 'Testing the bug fix for default parent discovery. This page was created to verify the fix is working.'
                            }
                        },
                        'id': 1
                    }
                    
                    async with session.post(url, json=request_data) as resp:
                        result = await resp.json()
                        print('📋 Page creation result:')
                        if 'result' in result:
                            content = result['result'].get('content', [])
                            if content:
                                text = content[0].get('text', 'No text')
                                print('  ✅ Success:', text)
                                if 'Successfully created page' in text:
                                    print('\n🎉 Bug fix is working! Page creation successful.')
                                    return True
                                else:
                                    print('\n⚠️ Unexpected response but no error.')
                                    return False
                            else:
                                print('  📝 Result:', result['result'])
                                return False
                        else:
                            error = result.get('error', 'Unknown error')
                            print('  ❌ Error:', error)
                            return False
                else:
                    print('❌ Server not accessible:', response.status)
                    return False
                    
    except Exception as e:
        print('❌ Error:', str(e))
        return False

async def main():
    success = await test_server()
    if success:
        print("\n✅ All tests passed! The bug fix is working correctly.")
    else:
        print("\n❌ Tests failed. The bug might still exist or server is not updated yet.")

if __name__ == "__main__":
    asyncio.run(main()) 