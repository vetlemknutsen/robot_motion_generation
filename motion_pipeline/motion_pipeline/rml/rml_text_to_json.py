import json
import subprocess
from pathlib import Path

from motion_pipeline.rml.parser_base import RMLParser


# Path to the Langium project that owns the real RML grammar/parser
# we shell out to its Node CLI instead of re-implementing parser
LANGIUM_ROOT = Path(__file__).resolve().parents[3] / "robot-motion-language"

# Parses and validates RML text via the Langium CLI
class LangiumRMLParser(RMLParser):
    def __init__(self, langium_root: Path = LANGIUM_ROOT):
        self.langium_root = langium_root

    # Run the Langium CLI as a subprocess: write RML to a temp file,
    # let the CLI produce JSON next to it, then read that JSON back in
    def parse(self, rml_text: str) -> dict: 
        # write the RML somewhere the CLI can find it
        input_rml = self.langium_root / "bridge_input.rml"
        input_rml.write_text(rml_text)

        # CLI always writes its output here
        output_json = self.langium_root / "generated" / "bridge_input.json"
        cli = self.langium_root / "bin" / "cli"

        # Run the Langium CLI as a subprocess. It parses AND validates the RML, 
        # then writes JSON. If the RML is invalid, the CLI exits non-zero and 
        # check= True turns that into a Python exception. 
        subprocess.run(["node", str(cli), "generate", str(input_rml)], cwd=self.langium_root, check=True)

        if output_json.exists():
            data = json.loads(output_json.read_text())
            # clean up the temp input so we don't leave junk
            input_rml.unlink(missing_ok=True)
            return data
        else:
            raise FileNotFoundError(f"Langium CLI did not create {output_json}")

