"""Three-bit token grammar. Only StateToken instances are operands."""
import csv
import io
import json
import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class _Bits:
    L: int
    F: int
    M: int

    def __post_init__(self):
        if any(type(bit) is not int or bit not in (0, 1) for bit in self.bits):
            raise ValueError("Each bit must be the integer 0 or 1.")

    @property
    def bits(self):
        return self.L, self.F, self.M

    def __str__(self):
        return "".join(map(str, self.bits))

    @classmethod
    def parse(cls, raw):
        if not isinstance(raw, str) or len(raw) != 3 or any(c not in "01" for c in raw):
            raise ValueError("Enter exactly three binary digits in L, F, M order.")
        return cls(*map(int, raw))


class StateToken(_Bits):
    pass


class TransitionToken(_Bits):
    pass


State = StateToken


@dataclass(frozen=True)
class Magnitude:
    value: int


@dataclass(frozen=True)
class Ratio:
    changed: int
    unchanged: int

    def __str__(self):
        return f"{self.changed}:{self.unchanged}"


@dataclass(frozen=True)
class Flow:
    value: float
    bce_term = "Flow’"
    standard_term = "state-change rate"


def finite(value):
    if type(value) not in (float, int, str) or not math.isfinite(float(value)):
        raise ValueError("Time and rate values must be finite numbers.")
    return float(value)


@dataclass(frozen=True)
class Timestamp:
    value: float

    def __post_init__(self):
        object.__setattr__(self, "value", finite(self.value))


@dataclass(frozen=True)
class Quality:
    name: str
    zero: str = "0"
    one: str = "1"


@dataclass(frozen=True)
class Lens:
    name: str = "Neutral"
    L: Quality = Quality("Location")
    F: Quality = Quality("Function")
    M: Quality = Quality("Magnitude")

    def interpret(self, state):
        return [q.one if bit else q.zero for q, bit in zip((self.L,self.F,self.M), state.bits)]


def require_state(state):
    if not isinstance(state, StateToken):
        raise TypeError("Expected a StateToken.")


def invert(state):
    require_state(state)
    return StateToken(*(1-bit for bit in state.bits))


def transition(a, b):
    require_state(a)
    require_state(b)
    return TransitionToken(*(x ^ y for x, y in zip(a.bits, b.bits)))


def hamming_distance(a, b):
    return Magnitude(sum(transition(a,b).bits))


def change_ratio(a, b):
    changed = hamming_distance(a,b).value
    return Ratio(changed, 3-changed)


def flow(a, b, delta_t):
    elapsed = finite(delta_t)
    if elapsed <= 0:
        raise ValueError("Elapsed time must be positive; timestamps must strictly increase.")
    return Flow(finite(hamming_distance(a,b).value / elapsed))


def label(value):
    if not isinstance(value,str) or not value.strip() or len(value)>100:
        raise ValueError("Labels must contain 1–100 characters.")
    return value.strip()


def session(payload):
    raw = payload["states"]
    if not isinstance(raw,list) or not 1 <= len(raw) <= 2000:
        raise ValueError("Enter between 1 and 2,000 states.")
    states = []
    for i, token in enumerate(raw,1):
        try:
            states.append(State.parse(token))
        except ValueError as exc:
            raise ValueError(f"State {i}: {exc}") from exc
    unit = label(payload.get("unit","tick"))
    t = payload.get("timestamps")
    tau = None
    if t is None:
        tau = finite(payload.get("tau",1))
        if tau <= 0:
            raise ValueError("Tick duration must be positive.")
        t = [i*tau for i in range(len(states))]
    if not isinstance(t,list) or len(t)!=len(states):
        raise ValueError("Supply one timestamp per state.")
    times = [Timestamp(v) for v in t]
    finite(times[-1].value-times[0].value)
    config = payload.get("lens",{})
    qualities = {}
    for key, default in zip("LFM",("Location","Function","Magnitude")):
        item = config.get(key,{})
        qualities[key] = Quality(*(label(item.get(k,v)) for k,v in
                                   (("name",default),("zero","0"),("one","1"))))
    lens = Lens(label(config.get("name","Neutral")), **qualities)
    metadata = asdict(lens)
    history = [dict(timestamp=time.value,state=str(state),interpretation=lens.interpret(state))
               for time,state in zip(times,states)]
    rows = []
    for i,(a,b) in enumerate(zip(states,states[1:])):
        start,end = times[i].value,times[i+1].value
        dt = end-start
        rate = flow(a,b,dt)
        ratio = change_ratio(a,b)
        rows.append(dict(timestamp=start,target_timestamp=end,source_state=str(a),target_state=str(b),
                         transition=str(transition(a,b)),inverse_source=str(invert(a)),inverse_target=str(invert(b)),
                         hamming_distance=ratio.changed,change_ratio=str(ratio),changed_fraction=ratio.changed/3,
                         delta_t=dt,flow=rate.value,time_unit=unit,lens_name=lens.name,lens_metadata=metadata))
    return dict(schema="ultimodel.tokens.v0.1",tau=tau,time_unit=unit,lens=metadata,history=history,rows=rows)


def csv_export(record):
    fields = ("timestamp","target_timestamp","source_state","target_state","transition","inverse_source",
              "inverse_target","hamming_distance","change_ratio","changed_fraction","delta_t","flow",
              "time_unit","lens_name","lens_metadata")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream,fields)
    writer.writeheader()
    for row in record["rows"]:
        writer.writerow({**row,"lens_metadata":json.dumps(row["lens_metadata"],ensure_ascii=False)})
    return stream.getvalue()
