"""Interprets RML JSON payloads into motor commands"""
class MotionInterpreter:

    def __init__(self, motors, sensors, sync_move_fn, sync_multimove):
        self.motors = motors
        self.sensors = sensors
        self.sync_move = sync_move_fn
        self.sync_multimove = sync_multimove

    def execute(self, payload: dict):
        for cmd in payload.get("commands", []):
            if "multimove" in cmd:
                self._multimove(cmd["multimove"])
            elif "move" in cmd:
                self._move(cmd["move"], sync=True)

    def _multimove(self, moves: list):
        goals = []
        for entry in moves: 
            move = entry.get("move", {})
            key, position = self._decode_move(move)
            if key not in self.motors:
                print(f"Unknown motor key: {key}")
                return
            if key not in self.sensors:
                print(f"Missing sensor key: {key}")
                return

            goals.append((self.motors[key], self.sensors[key], position))

        if goals:
            self.sync_multimove(goals)


    def _move(self, move: dict, sync: bool):
        key, position = self._decode_move(move)
        if key not in self.motors:
            print(f"Unknown motor key: {key}")
            return
        if key not in self.sensors:
            print(f"Missing sensor key: {key}")
            return

        if sync:
            self.sync_move(self.motors[key], self.sensors[key], position)
        else:
            self.motors[key].setPosition(position)


    def _build_key(self, side, joint, rotation):
        key = ""
        if side in ("right", "left"):
            key = side[0].upper()
        key += joint.capitalize() + (rotation.capitalize() if rotation else "")
        return key
    
    def _decode_move(self, move):
        side = move.get("side", "")
        joint = move.get("joint", "")
        rotation = move.get("rotation", "")
        position = move["position"]
        return self._build_key(side, joint, rotation), position
