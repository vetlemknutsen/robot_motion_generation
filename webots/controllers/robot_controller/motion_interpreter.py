class MotionInterpreter:
    """Turns RML JSON commands into Webots motor positions.
    Doesn't talk to Webots directly, it's given motor/sensor lookup
    dicts and a callback for setting positions synchronously. 
    This makes the interpreter easy to test and keeps Webots-specific code in
    RobotController.
    """

    def __init__(self, motors, sensors, sync_multimove):
        self.motors = motors                   # {joint_key: Webots motor device}
        self.sensors = sensors                 # {joint_key: Webots position sensor}
        self.sync_multimove = sync_multimove   # callback: drive many motors and block until all reached

    def execute(self, payload: dict):
        """Run all commands from one RML JSON payload, in order.
        Args:
            payload: Parsed RML JSON. Each command is either a "move"
                (single joint) or a "multimove" (joints that should
                move together).
        """
        for cmd in payload.get("commands", []):
            if "multimove" in cmd:
                self._multimove(cmd["multimove"])
            elif "move" in cmd:
                self._move(cmd["move"])

    # Move several joints at the same time and wait until they all arrive.
    # If any joint is missing a motor or sensor, abort the whole multimove
    # so we don't half-execute it.
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

        # only call the callback if goals
        if goals:
            self.sync_multimove(goals)

    # Single-joint move. Wraps as a one-element multimove so we only have
    # one execution path
    def _move(self, move: dict):
        self._multimove([{"move": move}])


    # Build a config-lookup key from RML fields.
    # Example: side="right", joint="shoulder", rotation="pitch" = "RShoulderPitch"
    # Matches the naming convention used in the per-robot YAML files.
    def _build_key(self, side, joint, rotation):
        key = ""
        if side in ("right", "left"):
            key = side[0].upper()
        key += joint.capitalize() + (rotation.capitalize() if rotation else "")
        return key

    
    # Pull side/joint/rotation/position out of a move dict and produce
    # the key + target position. Position is required. the rest default to "".
    def _decode_move(self, move):
        side = move.get("side", "")
        joint = move.get("joint", "")
        rotation = move.get("rotation", "")
        position = move["position"]
        return self._build_key(side, joint, rotation), position
