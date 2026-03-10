import json
import subprocess
from pathlib import Path

from motion_pipeline.rml.parser_base import RMLParser

LANGIUM_ROOT = Path(__file__).resolve().parents[3] / "robot-motion-language"


class LangiumRMLParser(RMLParser):
    def __init__(self, langium_root: Path = LANGIUM_ROOT):
        self.langium_root = langium_root

    def parse(self, rml_text: str) -> dict: 
        input_rml = self.langium_root / "bridge_input.rml"
        input_rml.write_text(rml_text)

        output_json = self.langium_root / "generated" / "bridge_input.json"
        cli = self.langium_root / "bin" / "cli"

        subprocess.run(["node", str(cli), "generate", str(input_rml)], cwd=self.langium_root, check=True)

        if output_json.exists():
            data = json.loads(output_json.read_text())
            input_rml.unlink(missing_ok=True)
            return data
        else:
            raise FileNotFoundError(f"Langium CLI did not create {output_json}")

