from motion_pipeline.adapters.demo import DemoAdapter
from motion_pipeline.runtime.pipeline import PipelineRunner
from motion_pipeline.emitter.emitter import BasicRMLEmitter

DEMO_INPUT = {
    "name": "simple_wave",
    "moves": [
        {"joint": "RShoulderPitch", "position": -1.5},
        {"joint": "RShoulderPitch", "position": 1.5},
    ],
}


def main() -> None:
    runner = PipelineRunner(DemoAdapter(), BasicRMLEmitter())
    rml_text = runner.run(DEMO_INPUT)

    print("RML")
    print(rml_text)


if __name__ == "__main__":
    main()
