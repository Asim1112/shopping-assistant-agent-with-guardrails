import os
from dotenv import load_dotenv
from agents import ( Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, GuardrailFunctionOutput,
input_guardrail, output_guardrail, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered )
import asyncio
from pydantic import BaseModel

load_dotenv()

GEMINI_UPPER_MODEL = "gemini-2.5-flash"
GEMINI_LOWER_MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


class DetectIllegalQueryOutput(BaseModel):
    is_illegal_query: bool
    reasoning: str

class DetectSensitiveAdviceOutput(BaseModel):
    is_sensitive_advice: bool
    reasoning: str

class MessageOutput(BaseModel):
    response: str



async def main():

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not found in .env file")

    gemini_client = AsyncOpenAI(
        api_key = GEMINI_API_KEY,
        base_url = BASE_URL
    )

    gemini_premium_model = OpenAIChatCompletionsModel(
        openai_client = gemini_client,
        model = GEMINI_UPPER_MODEL
    )

    gemini_cheap_model = OpenAIChatCompletionsModel(
        openai_client = gemini_client,
        model = GEMINI_LOWER_MODEL
    )

    
    illegal_query_input_guardrail = Agent(
        name = "input guardrail agent",
        instructions = """
        You are an input guardrail agent. Your job is to detect if the user's query is
        about illegal or restricted products like weapons, drugs, narcotics, or anything
        that violates standard policies.
        """,
        output_type = DetectIllegalQueryOutput,
        model = gemini_cheap_model
    )

    sensitive_advice_output_guardrail = Agent(
        name = "output_guardrail_agent",
        instructions = """
        You are an output guardrail agent. Your job is to check if the main agent's response
        gives any kind of medical or financial advice. Flag it if so.
        """,
        output_type = DetectSensitiveAdviceOutput,
        model = gemini_cheap_model
    )


    @input_guardrail
    async def illegal_query(ctx, agent, input):
        result = await Runner.run(starting_agent = illegal_query_input_guardrail, input = input)
        print(result.final_output)
        
        return GuardrailFunctionOutput(
            output_info = result.final_output,
            tripwire_triggered = result.final_output.is_illegal_query
        )
    

    @output_guardrail
    async def sensitive_advice(ctx, agent, output):
        result = await Runner.run(starting_agent = sensitive_advice_output_guardrail, input = output.response)

        # print(result.final_output)
        
        return GuardrailFunctionOutput(
            output_info = result.final_output,
            tripwire_triggered = result.final_output.is_sensitive_advice
        )



    ShoppingAssistant = Agent(
        name = "shopping assistant agent",
        instructions = """
        You are a friendly shopping assistant. Help users discover new products,
        compare options, share shopping tips, and guide them to find good deals. 
        DO NOT give medical or financial advice.
        """,
        output_type = MessageOutput,
        model = gemini_premium_model,
        input_guardrails = [illegal_query],
        output_guardrails = [sensitive_advice]
    )


    try:
        result = await Runner.run(
            starting_agent = ShoppingAssistant, 
            input = "Should I invest in cryptocurrency right now?"
        )
        
        print(result.final_output)

    
    except InputGuardrailTripwireTriggered:
        print("That's not something I can assist with. Feel free to ask about products, deals, or shopping tips!")

    
    except OutputGuardrailTripwireTriggered:
        print("I recommend speaking to a licensed professional for that kind of advice. I'm here to help with shopping questions only!")


 




if __name__ == "__main__":
    asyncio.run(main())



