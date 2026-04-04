## /home/dhankar/temp/26_04/claude_certs/multi_tool_calls__4_4.py

from dotenv import load_dotenv
load_dotenv()

import json
import jsonschema
from datetime import datetime, timedelta
from pathlib import Path

from anthropic import Anthropic
from rich.console import Console
from anthropic.types import Message

console = Console()

MODEL = "claude-haiku-4-5"
SCHEMA_DIR = Path(__file__).parent / "json_schema"

system_prompt_maths_tutor = """you are a patient math tutor , 
always respond with the Math answer and a Shakespare Quote , 
Highlight the Philosphical Quote on a 
separate line -- make it dramatic , we like DARK Humor with Maths"""

# ─────────────────────────────────────────────
# AGENT_TOOLS_LIST  (display index → schema key)
# ─────────────────────────────────────────────
AGENT_TOOLS_LIST = {
    "1": {"label": "DATE_TOOL     — get current date/time",     "schema": "get_current_datetime"},
    "2": {"label": "TIME_TOOL     — add duration to a datetime", "schema": "add_duration_to_datetime"},
    "3": {"label": "CALENDAR_TOOL — set a reminder",            "schema": "set_reminder"},
    "4": {"label": "BATCH_TOOL    — invoke multiple tools",     "schema": "batch_tool"},
}

system_prompt_maths_tutor_with_tools = f"""
you are math tutor with other tools and tasks, 
only respond with the Math answer if asked for,  

IMPORTANT -Now you have additional TOOLS , 
you Now need to Validate the USER INPUT and check if a TOOL From 
your {AGENT_TOOLS_LIST} can be used for the USER QUERY """




# ─────────────────────────────────────────────
# UtilToolCalls — utility / tool implementations
# ─────────────────────────────────────────────

class UtilToolCalls:

    @staticmethod
    def get_current_datetime():
        """ 
        """
        pass

    @staticmethod
    def add_duration_to_datetime(datetime_str, 
                                 duration=0, 
                                 unit="days", 
                                 input_format="%Y-%m-%d"
                                    ):
        """ 
        """
        
        date = datetime.strptime(datetime_str, input_format)
        if unit == "seconds":
            new_date = date + timedelta(seconds=duration)
        elif unit == "minutes":
            new_date = date + timedelta(minutes=duration)
        elif unit == "hours":
            new_date = date + timedelta(hours=duration)
        elif unit == "days":
            new_date = date + timedelta(days=duration)
        elif unit == "weeks":
            new_date = date + timedelta(weeks=duration)
        elif unit == "months":
            month = date.month + duration
            year = date.year + month // 12
            month = month % 12
            if month == 0:
                month = 12
                year -= 1
            day = min(
                date.day,
                [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
                 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1],
            )
            new_date = date.replace(year=year, month=month, day=day)
        elif unit == "years":
            new_date = date.replace(year=date.year + duration)
        else:
            raise ValueError(f"Unsupported time unit: {unit}")
        return new_date.strftime("%A, %B %d, %Y %I:%M:%S %p")

    @staticmethod
    def set_reminder(content, timestamp):
        console.print(f"[bold yellow]----[/bold yellow]")
        console.print(f"[yellow]Setting reminder for {timestamp}:[/yellow]")
        console.print(f"[yellow]{content}[/yellow]")
        console.print(f"[bold yellow]----[/bold yellow]")

    @staticmethod
    def validate_json_schema(schema: dict) -> bool:
        """
        Validates a tool schema dict against the JSON Schema Draft-7 meta-schema.
        Returns True if valid, raises jsonschema.ValidationError if not.
        """
        meta_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["name", "description", "input_schema"],
            "properties": {
                "name":         {"type": "string"},
                "description":  {"type": "string"},
                "input_schema": {"type": "object"},
            },
        }
        jsonschema.validate(instance=schema, schema=meta_schema)
        return True

    @staticmethod
    def text_from_message(message):
        return "\n".join([block.text for block in message.content if block.type == "text"])

# ─────────────────────────────────────────────
# MultiToolCalls — agent orchestrator
# ─────────────────────────────────────────────
class MultiToolCalls:

    def __init__(self):
        self.client = Anthropic()
        self.model = MODEL
        self.messages = []
        self.util = UtilToolCalls()
        self.schemas = self._load_schemas()

    # ── schema loader ──────────────────────────
    def _load_schemas(self) -> dict:
        schemas = {}
        for entry in AGENT_TOOLS_LIST.values():
            key = entry["schema"]
            path = SCHEMA_DIR / f"{key}.json"
            with open(path) as f:
                schema = json.load(f)
            UtilToolCalls.validate_json_schema(schema)   # validate on load
            schemas[key] = schema
        return schemas

    # ── core chat call ─────────────────────────
    def chat(self, messages, system=None, tools=None):
        params = {
                    "model": self.model,
                    "max_tokens": 1000,
                    "messages": messages,
                }
        if system:
            params["system"] = system
        if tools:
            params["tools"] = tools
        return self.client.messages.create(**params)

    # ── tool dispatcher ────────────────────────
    def process_tool_call(self, tool_name: str, tool_input: dict) -> str:
        console.print("[bold cyan]=======tool_input========[/bold cyan]")
        console.print(f"[cyan]  {tool_input} [/cyan]")

        if tool_name == "get_current_datetime":
            return self.util.get_current_datetime()
            # fmt = tool_input.get("date_format", "%Y-%m-%d %H:%M:%S")
            # return datetime.now().strftime(fmt)

        elif tool_name == "add_duration_to_datetime":
            return self.util.add_duration_to_datetime(
                datetime_str=tool_input["datetime_str"],
                duration=tool_input.get("duration", 0),
                unit=tool_input.get("unit", "days"),
                input_format=tool_input.get("input_format", "%Y-%m-%d"),
            )

        elif tool_name == "set_reminder":
            self.util.set_reminder(tool_input["content"], tool_input["timestamp"])
            return f"Reminder set for {tool_input['timestamp']}"

        elif tool_name == "batch_tool":
            results = []
            for inv in tool_input.get("invocations", []):
                args = json.loads(inv["arguments"])
                results.append(self.process_tool_call(inv["name"], args))
            return "\n".join(results)

        return f"Unknown tool: {tool_name}"

    # ── agentic loop ───────────────────────────
    def run_agent_loop(self, user_input, 
                       system_prompt: str, 
                       tools: list) -> str:
        """ 
        """
        from anthropic.types import Message
        user_message = user_input.content if isinstance(user_input, Message) else user_input

        self.messages.append({"role": "user", "content": user_message})
        while True:
            response = self.chat(self.messages, 
                                 system=system_prompt, 
                                 tools=tools)
            
            if response.stop_reason == "end_turn":
                final_text = "\n".join(
                                        b.text for b in response.content if hasattr(b, "text")
                                    )
                self.messages.append({"role": "assistant", "content": response.content})
                return final_text

            # handle tool_use
            self.messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    console.print(f"[dim]>> tool_use: {block.name}({block.input})[/dim]")
                    result = self.process_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })
            self.messages.append({"role": "user", "content": tool_results})

    # ── tool selection menu ────────────────────
    def display_agent_tools(self) -> list:
        console.print()
        console.print("[bold cyan]=========================[/bold cyan]")
        console.print("[bold cyan]  AGENT TOOLS AVAILABLE  [/bold cyan]")
        console.print("[bold cyan]=========================[/bold cyan]")
        for num, entry in AGENT_TOOLS_LIST.items():
            console.print(f"[cyan]  {num}. {entry['label']}[/cyan]")
        console.print("[bold cyan]=========================[/bold cyan]")
        choice = console.input(
            "[cyan]Choose tool(s) [1-4], comma-separated, or 'all': [/cyan]"
        ).strip().lower()

        if choice == "all":
            keys = [e["schema"] for e in AGENT_TOOLS_LIST.values()]
        else:
            keys = []
            for c in choice.split(","):
                c = c.strip()
                if c in AGENT_TOOLS_LIST:
                    keys.append(AGENT_TOOLS_LIST[c]["schema"])
        return [self.schemas[k] for k in keys if k in self.schemas]


# ─────────────────────────────────────────────
# Chat loop
# ─────────────────────────────────────────────
def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})

def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})


def wrapper_get_user_input():
    """
    Continuous multi-tool chat loop.
    At each turn: display tool menu → user picks tools → 
    user types task → agent responds.
    Type 'exit' or 'quit' to stop.
    """

    agent = MultiToolCalls()

    while True:
        selected_tools = agent.display_agent_tools()
        user_input = console.input("\n[bold bright_green]You: [/bold bright_green]")
        if user_input.strip().lower() in ("exit", "quit"):
            console.print("[bold bright_green]Exiting chat.[/bold bright_green]")
            break
        answer = agent.run_agent_loop(user_input, 
                                      system_prompt=system_prompt_maths_tutor_with_tools, 
                                      tools=selected_tools)
        console.print("[bold bright_blue]---Assistant---[/bold bright_blue]")
        console.print(f"[bright_blue]{answer}[/bright_blue]")
        console.print()


if __name__ == "__main__":
    wrapper_get_user_input()
