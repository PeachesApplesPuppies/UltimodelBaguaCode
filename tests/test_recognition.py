import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4
from core.resonance import analyze, stress, sequence, ratio, PHI
from core.recognitions import operate, export_csv


class Resonance(unittest.TestCase):
    def test_required_geometry(self):
        f=dict(ratio_A="10:6.18",ratio_B="5:3.09",hypothesis="Phi",tolerance="0.01")
        c=analyze(f,"wing","reference")
        self.assertTrue(c["tests"]["normalized_pair"])
        self.assertEqual(c["A"]["ratio"]["normalized_ratio"],"1:309/500")
        self.assertNotEqual(c["A"]["ratio"]["raw_ratio"],c["B"]["ratio"]["raw_ratio"])
        self.assertTrue(c["tests"]["A_within_phi_tolerance"])
        self.assertAlmostEqual(c["A"]["phi_test"]["absolute_error"],10/6.18-PHI)
        self.assertTrue(stress(f)["both_inverted"])
        self.assertFalse(stress(f)["only_B_inverted"])
        self.assertTrue(stress(f)["independently_scaled"])
        self.assertEqual(analyze({**f,"ratio_A":"10:4"},"a","b")["suggested_status"],"Broken Rhyme")
        self.assertIsNone(analyze({**f,"tolerance":""},"a","b")["tests"]["A_within_phi_tolerance"])

    def test_recurrence(self):
        s=sequence("1:3,1:4,1:3,1:2,1:3,1:8,1:4")
        self.assertIsNone(s["observed_period"])
        self.assertEqual(s["frequency"]["1:3"],3)
        self.assertEqual(sequence("A,B,A,B,A")["observed_period"],2)

    def test_tokens_and_components(self):
        f=dict(token_A="101",token_B="111",token_lens_A="door",token_lens_B="door",
               token_confidence_A=".7",token_confidence_B=".8",elapsed="2",operator_A="rotation",operator_B="reflection")
        c=analyze(f,"a","b")
        self.assertEqual(c["token_comparison"]["xor"],"010")
        self.assertEqual(c["token_comparison"]["flow"],0.5)
        self.assertEqual(c["similarity_score"]["operator"],0)
        self.assertIsNone(c["similarity_score"]["semantic"])
        self.assertIsNone(analyze({**f,"token_lens_B":"another"},"a","b")["similarity_score"]["token"])

    def test_boundaries(self):
        self.assertIsNone(ratio("0:4","Forward")["normalized_ratio"])
        self.assertIsNone(ratio("4:0","Forward")["quotient"])
        self.assertIsNone(stress({"ratio_A":"4:0","ratio_B":"3:0"})["both_inverted"])
        self.assertEqual(ratio("4:8","Forward")["normalized_ratio"],ratio("3:6","Forward")["normalized_ratio"])


class Journal(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db=Path(tmp.name)/"journal.db"

    def call(self,action,**kw):
        return operate({"request":str(uuid4()),"action":action,**kw},self.db)

    def capture(self,text):
        return self.call("capture",observation=text,reference="old idea")

    def review(self,event,**form):
        return self.call("challenge",event=event["event"],revision=event["history"][-1]["seq"],form=form)

    def test_history_and_failures(self):
        first=self.capture("  suddenly\nI saw it.  ")
        second=self.review(first,ratio_A="10:4",hypothesis="Phi",tolerance="1")
        last=self.review(second,ratio_A="10:6.18",hypothesis="Phi",tolerance="1")
        self.assertEqual(last["history"][:1],first["history"])
        self.assertEqual(last["history"][0]["data"]["source_observation"],"  suddenly\nI saw it.  ")
        self.assertEqual(len(self.call("catalog")["broken"]),1)
        rows=list(csv.DictReader(io.StringIO(export_csv(last))))
        self.assertEqual([int(r["sequence_number"]) for r in rows],[1,2,3])
        self.assertEqual(json.loads(rows[1]["data_json"])["verification_status"],"Broken Rhyme")
        with self.assertRaises(ValueError):
            self.review(first)
        stage=self.call("stage",event=last["event"],revision=3,stage="Explicit idea",note="recalled later")
        self.assertEqual(len(stage["history"]),4)

    def test_family(self):
        a,b=self.capture("A"),self.capture("B")
        members=[a["event"],b["event"]]
        fields=dict(name="One to two",members=members,independence="separate recordings")
        with self.assertRaises(ValueError):
            self.call("family",**fields)
        form=dict(source_domain="music",reference_domain="diagram",prompt="saw diagram",capture_lens="length",
                  discarded="absolute scale",invariant="1:2",ratio_A="2:4",ratio_B="1:2")
        self.review(a,**form,reference_id=b["event"])
        self.review(b,**form)
        self.call("family",**fields)
        self.assertEqual(len(self.call("catalog")["families"][0]["members"]),2)

    def test_retry(self):
        request=str(uuid4())
        a=self.call("capture",request=request,observation="text",reference="memory")
        b=self.call("capture",request=request,observation="text",reference="memory")
        self.assertEqual(a,b)
