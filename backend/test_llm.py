"""Quick test script for LLM connectivity. Does not print API keys."""
import asyncio
from app.services.llm_service import get_chat_model


async def main():
    try:
        llm = get_chat_model()
        print(f"Model: {llm.model_name}")
        print(f"Base URL: {llm.root_client.base_url}")
        print()
        print("Invoking LLM with: 'Say hello in one word'")
        result = await llm.ainvoke("Say hello in one word")
        print(f"SUCCESS! Response: {result.content}")
    except Exception as e:
        print(f"FAILED!")
        print(f"  Type: {type(e).__module__}.{type(e).__name__}")
        print(f"  Message: {e}")
        # Print cause chain
        cause = e.__cause__
        depth = 1
        while cause and depth < 5:
            print(f"  Caused by [{depth}]: {type(cause).__module__}.{type(cause).__name__}: {cause}")
            cause = cause.__cause__ or cause.__context__
            depth += 1


if __name__ == "__main__":
    asyncio.run(main())
