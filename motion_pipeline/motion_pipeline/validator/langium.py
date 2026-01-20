import subprocess
import tempfile
from pathlib import Path

# Validates the RML generated, reuses old langium CLI
class LangiumRMLValidator:
    def __init__(self, langium_root: Path) -> None:
        self.langium_root = Path(langium_root)

    def validate(self, rml_text: str) -> None:
        # Langium only accepts files, make temporary rml file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".rml", delete=False) as tmp:
            tmp.write(rml_text)
            tmp_path = Path(tmp.name)

        try:
            subprocess.run(
                ["npx", "robot-motion-language-cli", "parseAndValidate", str(tmp_path)],
                cwd=self.langium_root,
                check=True,
            )
        #deletes temp .rml file
        finally:
            tmp_path.unlink(missing_ok=True)
