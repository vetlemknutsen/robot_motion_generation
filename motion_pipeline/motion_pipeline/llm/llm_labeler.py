import json
from motion_pipeline.llm.base import Labeler
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv 

# load API key from the .env at the repo root
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)


class LLMLabeler(Labeler): 
    # Add "// intent: " comments above each multimove block in RML text.
    # If anything fails, just return the original text unchanged. 
    def label_code(self, rml_text:str, robot_key: str) -> str: 
        try: 
            labels = self._get_labels(rml_text, robot_key)
            lines = rml_text.split("\n")
            result = []
            label_index = 0 

            for line in lines: 
                # insert a label comment right before each multimove block
                if line.strip().startswith("multimove") and label_index < len(labels):
                    # match the indentation of hte multimove line so it looks good
                    indent = line[:len(line) - len(line.lstrip())]
                    result.append(f"{indent}// intent: {labels[label_index]}")
                    label_index += 1
                result.append(line)

            return "\n".join(result)
        except Exception as e:
            # On any failure, return original RML so the pipeline still works
            return rml_text


    # ask the LLM to label each multimove block with its high-level intent
    # returns a list of labels in order
    def _get_labels(self, rml_text: str, robot_key: str) -> list[str]:
        prompt_text = f""" 
                You are analyzing robot motion language (RML) code that controls a robot arm for the robot {robot_key}
                The code contains multiple "multimove" blocks executed in sequence.

                Analyze the entire motion trajectory before labeling any block.
                Identify the higher-level intent of each block based on its role in the 
                overall sequence.

                Respond with ONLY a JSON object like {{"labels": ["reach", "grab", "release", "...one per multimove block in order"]]}}, one label per multimove block,
                in the order they appear. 
                For the robot Tiago, the gripper is closed when left and right finger joints are at 0.
                """

        try:
            client = OpenAI()
            content = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_text},
                    {"role": "user", "content": rml_text}
                ],
                temperature=0, # deterministic
                response_format={"type": "json_object"} # force json for parsing
            )
        except Exception as e:
            # if API call fails, return no labels and skip labeling
            return []

        content = content.choices[0].message.content
        return json.loads(content)["labels"]
