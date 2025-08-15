import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced

async def quick_test():
    agent = IntelligenceAgentEnhanced()
    
    print('Testing: Find me sleeper candidates')
    print('-'*50)
    
    try:
        response = await agent.process_message('Find me sleeper candidates')
        
        if response and response.content:
            print(f'Response length: {len(response.content)} chars')
            print(f'\nFirst 2000 chars of response:')
            print('='*50)
            print(response.content[:2000])
            if len(response.content) > 2000:
                print(f'\n... [{len(response.content) - 2000} more characters]')
        else:
            print('No response or empty content')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_test())