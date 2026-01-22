import json
import subprocess
from pathlib import Path

LANGIUM_ROOT = Path(__file__).resolve().parents[3] / "robot-motion-language"


def rml_text_to_legacy_payload(rml_text: str, langium_root: Path = LANGIUM_ROOT) -> dict:

    input_rml = langium_root / "bridge_input.rml"
    input_rml.write_text(rml_text)

    output_json = langium_root / "generated" / "bridge_input.json"

    cli = langium_root / "bin" / "cli"

    cmd = ["node", str(cli), "generate", str(input_rml)]

    subprocess.run(cmd, cwd=langium_root, check=True)

    if output_json.exists():
        data = json.loads(output_json.read_text())
        input_rml.unlink(missing_ok=True)
        return data
    else:
        raise FileNotFoundError(f"Langium CLI did not create {output_json}")