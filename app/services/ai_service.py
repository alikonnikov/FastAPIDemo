import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.models.task import TaskSuggestion

async def get_ai_task_suggestion(text: str) -> TaskSuggestion:
    # If key is default or missing, use mock
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_key":
        return TaskSuggestion(
            title=f"Refined: {text[:50]}...",
            description=f"Automated description based on: {text}",
            priority="high" if "fail" in text.lower() or "bug" in text.lower() else "medium",
            tags=["backend", "auto-generated"]
        )

    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        system_prompt = (
            "You are an expert project manager. Convert messy task descriptions into professional, structured tasks. "
            "Return ONLY a JSON object with: 'title' (max 60 chars), 'description' (clear and actionable), "
            "'priority' (must be one of: 'low', 'medium', 'high'), and 'tags' (list of 2-4 strings)."
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini as a cost-effective and fast default
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return TaskSuggestion(**data)
        
    except Exception as e:
        # Log error and return a basic fallback to prevent total failure
        print(f"AI Service Error: {str(e)}")
        return TaskSuggestion(
            title=f"Task: {text[:50]}",
            description=f"Processed text: {text}. Note: AI processing failed, returned fallback.",
            priority="medium",
            tags=["manual-check"]
        )

async def call_llm_api(text: str):
    # This can be used for more custom logic if needed
    return await get_ai_task_suggestion(text)
