import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv 
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)


class LLMLabeler: 
    def label_code(self, rml_text:str, robot_key: str) -> str: 
        try: 
            labels = self._get_labels(rml_text, robot_key)
            lines = rml_text.split("\n")
            result = []
            label_index = 0 

            for line in lines: 
                if line.strip().startswith("multimove") and label_index < len(labels):
                    indent = line[:len(line) - len(line.lstrip())]
                    result.append(f"{indent}// intent: {labels[label_index]}")
                    label_index += 1
                result.append(line)

            return "\n".join(result)
        except Exception as e:
            return rml_text



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
                temperature=0,
                response_format={"type": "json_object"}
            )
        except Exception as e:
            return []

        content = content.choices[0].message.content
        return json.loads(content)["labels"]
