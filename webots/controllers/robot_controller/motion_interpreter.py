"""Interprets RML JSON payloads into motor commands"""
class MotionInterpreter:

    def __init__(self, motors, sensors, sync_move_fn):
        self.motors = motors
        self.sensors = sensors
        self.sync_move = sync_move_fn

    def execute(self, payload: dict):
        for cmd in payload.get("commands", []):
            if "multimove" in cmd:
                self._multimove(cmd["multimove"])
            elif "move" in cmd:
                self._move(cmd["move"], sync=True)

    def _multimove(self, moves: list):
        for i, entry in enumerate(moves):
            sync = (i + 1 == len(moves))
            self._move(entry["move"], sync=sync)

    def _move(self, move: dict, sync: bool):
        side = move.get("side", "")
        joint = move.get("joint", "").capitalize()
        rotation = move.get("rotation", "")
        if rotation:
            rotation = rotation.capitalize()
        position = move["position"]

        key = ""
        if side in ("right", "left"):
            key = side[0].upper()
        key += joint + rotation

        if key not in self.motors:
            print(f"Unknown motor key: {key}")
            return

        if sync:
            self.sync_move(self.motors[key], self.sensors[key], position)
        else:
            self.motors[key].setPosition(position)
