from typing import Any, Sequence, Tuple

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.schema import Program
from motion_pipeline.emitter.emitter import BasicRMLEmitter


class PipelineRunner:
    def __init__(self, adapter: Adapter, emitter: BasicRMLEmitter):
        self.adapter = adapter
        self.emitter = emitter

    def run(self, source: Any) -> str:
        program = self.adapt(source)
        rml_text = self.emitter.emit(program)
        return rml_text

    def adapt(self, source: Any) -> Program:
        return self.adapter.to_program(source)
