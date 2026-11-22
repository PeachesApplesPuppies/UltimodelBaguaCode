import csv
import io
import itertools
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from app import Handler
from core.tokens import (State, TransitionToken, Timestamp, Magnitude, Flow, Ratio,
                         invert, transition, hamming_distance, change_ratio, flow,
                         session, csv_export)


class TokenGrammar(unittest.TestCase):
    def test_every_ordered_pair(self):
        for i,j in itertools.product(range(8), repeat=2):
            a,b = (State.parse(format(n,"03b")) for n in (i,j))
            mask = i ^ j
            count = mask.bit_count()
            self.assertEqual(str(transition(a,b)),format(mask,"03b"))
            self.assertEqual(hamming_distance(a,b),Magnitude(count))
            self.assertEqual(change_ratio(a,b),Ratio(count,3-count))
            self.assertEqual(flow(a,b,1),Flow(count))
            self.assertEqual(str(invert(a)),format(7-i,"03b"))
            self.assertEqual(invert(invert(a)),a)

    def test_separate_types(self):
        state,mask=State(0,0,1),TransitionToken(0,0,1)
        self.assertNotEqual(state,mask)
        self.assertNotEqual(Magnitude(1),Flow(1))
        for fn in (lambda: invert(mask),lambda: transition(mask,state),lambda: flow(state,state,Timestamp(1))):
            with self.assertRaises((TypeError,ValueError)):
                fn()

    def test_invalid_input(self):
        for raw in (None,101,"1","0110","0x1"," 10","２01"):
            with self.assertRaises(ValueError):
                State.parse(raw)
        for bit in (2,True,1.0,"0"):
            with self.assertRaises(ValueError):
                State(bit,0,0)

    def test_sequence(self):
        result=session({"states":["000","001","101","111"]})
        self.assertEqual([r["transition"] for r in result["rows"]],["001","100","010"])
        self.assertEqual([r["hamming_distance"] for r in result["rows"]],[1,1,1])
        self.assertEqual([p["timestamp"] for p in result["history"]],[0,1,2,3])

    def test_clock(self):
        for params,expected in [({},3),({"tau":3},1),({"timestamps":[-2,4]},0.5)]:
            result=session({"states":["000","111"],**params})
            self.assertEqual(result["rows"][0]["flow"],expected)
        for config in ({"timestamps":[1,1]},{"timestamps":[1,-1]},{"timestamps":[0]},
                       {"tau":0},{"tau":"nan"},{"tau":"inf"},{"timestamps":[0,1e-320]}):
            with self.assertRaises(ValueError):
                session({"states":["000","111"],**config})

    def test_lens_and_csv(self):
        base={"states":["000","100"],"unit":"frame"}
        lens={"name":"A, B","L":{"name":"Side","zero":"Inside","one":"Outside"}}
        neutral=session(base)
        custom=session({**base,"lens":lens})
        self.assertEqual(custom["history"][1]["interpretation"][0],"Outside")
        for key in ("transition","target_state","flow","change_ratio"):
            self.assertEqual(custom["rows"][0][key],neutral["rows"][0][key])
        row=next(csv.DictReader(io.StringIO(csv_export(custom))))
        self.assertEqual(row["source_state"],"000")
        self.assertEqual(json.loads(row["lens_metadata"]),custom["lens"])
        self.assertEqual(row["time_unit"],"frame")

    def test_single_state(self):
        result=session({"states":["010"]})
        self.assertEqual(len(result["history"]),1)
        self.assertEqual(result["rows"],[])
        self.assertEqual(len(csv_export(result).splitlines()),1)


class HttpRoutes(unittest.TestCase):
    def test_workspace(self):
        class QuietHandler(Handler):
            def log_message(self,*args):
                pass
        server=ThreadingHTTPServer(("127.0.0.1",0),QuietHandler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            root=f"http://127.0.0.1:{server.server_port}"
            self.assertIn('/tokens',urlopen(root).read().decode())
            self.assertIn('Lens’ editor',urlopen(root+'/tokens').read().decode())
            def post(route, payload):
                return urlopen(Request(root+route,data=json.dumps(payload).encode()))
            payload={"states":["101","111"],"timestamps":[2,6]}
            self.assertEqual(json.load(post('/api/tokens',payload))["rows"][0]["flow"],0.25)
            self.assertIn('010',post('/api/tokens.csv',payload).read().decode())
            with self.assertRaises(HTTPError) as caught:
                post('/api/tokens',{"states":["xyz"]})
            self.assertEqual(caught.exception.code,400)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
