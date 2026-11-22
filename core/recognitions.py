"""Append-only local journal. One SQLite transaction per user action."""
import csv
import io
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict
from uuid import UUID, uuid4
from .resonance import analyze, stress, STATUSES

FIELDS = ("source_domain reference_domain suspected_pattern suspected_ratio suspected_geometry "
          "suspected_periodicity suspected_transformation confidence_initial emotional_salience notes "
          "image_reference equation_reference music_reference game_reference story_reference physical_object_reference").split()


class RecognitionEvent(TypedDict, total=False):
    timestamp: str
    source_observation: str
    candidate_reference: str
    immediate_description: str
    verification_status: str


class RelationshipFamily(TypedDict):
    id: str
    name: str
    members: list
    independence: str
    timestamp: str


def rows(db,event):
    result=[dict(r) for r in db.execute("SELECT * FROM journal WHERE event=? ORDER BY seq",(event,))]
    for row in result:
        row["data"]=json.loads(row["data"])
    return result


def catalog(db):
    events=[]
    broken=[]
    families=[]
    for row in db.execute("SELECT * FROM journal ORDER BY seq"):
        d=json.loads(row["data"])
        if row["kind"]=="capture":
            events.append(dict(id=row["event"],timestamp=row["stamp"],observation=d["source_observation"]))
        elif row["kind"]=="family":
            families.append(d)
        elif "Broken Rhyme" in (d.get("verification_status"),d.get("candidate",{}).get("suggested_status")):
            broken.append(dict(id=row["event"],revision=row["seq"],timestamp=row["stamp"],reason=d["form"].get("counterevidence","")))
    return dict(events=events,broken=broken,families=families)


def operate(p, path=None):
    path=Path(path or os.environ.get("BCE_RECOGNITION_DB",Path.home()/".bce-ultimodel"/"recognitions.sqlite3"))
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path,timeout=10)
    db.row_factory=sqlite3.Row
    try:
        with db:
            db.execute("CREATE TABLE IF NOT EXISTS journal(seq INTEGER PRIMARY KEY,event TEXT, stamp TEXT,kind TEXT,request TEXT UNIQUE,data TEXT)")
            action=p["action"]
            if action=="catalog":
                return catalog(db)
            event=p.get("event","")
            if action=="read":
                history=rows(db,event)
                if not history:
                    raise ValueError("Unknown event.")
                return dict(event=event,history=history)
            db.execute("BEGIN IMMEDIATE")
            request=str(UUID(p["request"]))
            prior=db.execute("SELECT event FROM journal WHERE request=?",(request,)).fetchone()
            if prior:
                return dict(event=prior["event"],history=rows(db,prior["event"]))
            now=datetime.now(timezone.utc).isoformat(timespec="microseconds")
            if action=="capture":
                observation,reference=p["observation"],p["reference"]
                if not all(isinstance(x,str) and x.strip() for x in (observation,reference)):
                    raise ValueError("Enter both your observation and what it reminded you of.")
                event=str(uuid4())
                data: RecognitionEvent={k:None for k in FIELDS}
                data.update(timestamp=now,source_observation=observation,candidate_reference=reference,
                            immediate_description=observation,verification_status="Unexamined",capture_lens="unspecified",
                            stage="first sensation and first association")
            elif action=="family":
                ids=list(dict.fromkeys(p["members"]))
                if len(ids)<2 or not p["name"].strip() or not p["independence"].strip():
                    raise ValueError("Choose at least two events, name the family and document independent observation.")
                members=[]
                for member in ids:
                    history=rows(db,member)
                    reviews=[r for r in history if "candidate" in r["data"]]
                    if not reviews:
                        raise ValueError("Each member needs a saved investigation.")
                    review=reviews[-1]
                    d=review["data"]
                    f=d["form"]
                    if d["verification_status"] not in ("Normalized Match","Validated Under Current Model","Structurally Similar") or not all(f.get(k,"").strip() for k in ("source_domain","reference_domain","invariant","discarded","prompt","capture_lens")):
                        raise ValueError("Members need a supported review, both domains, prompt, capture Lens’, discarded information and invariant.")
                    if d["candidate"]["suggested_status"] in ("Broken Rhyme","Unexamined"):
                        raise ValueError("Family admission requires a passed primary comparison.")
                    members.append(dict(event=member,review=review["seq"],invariant=f["invariant"].strip()))
                if len({m["invariant"].casefold() for m in members})!=1:
                    raise ValueError("Members must name the same invariant.")
                event=str(uuid4())
                data=RelationshipFamily(id=event,name=p["name"],members=members,independence=p["independence"],timestamp=now)
            else:
                history=rows(db,event)
                if not history or history[0]["kind"]!="capture":
                    raise ValueError("Choose an observation.")
                if p.get("revision")!=history[-1]["seq"]:
                    raise ValueError("This event changed. Reopen it before saving.")
                capture=history[0]["data"]
                if action=="stage":
                    if not p["note"].strip():
                        raise ValueError("Enter the stage observation.")
                    data=dict(stage=p["stage"],note=p["note"])
                elif action in ("review","challenge"):
                    f=p["form"]
                    ref=f.get("reference_id")
                    target=capture["candidate_reference"]
                    if ref:
                        other=rows(db,ref)
                        if ref==event or not other or other[0]["kind"]!="capture":
                            raise ValueError("Select a different source event.")
                        target=other[0]["data"]["source_observation"]
                    candidate=analyze(f,capture["source_observation"],target)
                    status=candidate["status"]
                    if status not in STATUSES:
                        raise ValueError("Unknown classification.")
                    if status=="Validated Under Current Model" and (candidate["suggested_status"] in ("Broken Rhyme","Unexamined") or not f.get("evidence","").strip()):
                        raise ValueError("Model validation requires a passed primary test and recorded evidence.")
                    challenge=stress(f) if action=="challenge" else None
                    data=dict(form=f,candidate=candidate,verification_status=status,challenge=challenge)
                else:
                    raise ValueError("Unknown journal action.")
            db.execute("INSERT INTO journal(event,stamp,kind,request,data) VALUES(?,?,?,?,?)",
                       (event,now,action,request,json.dumps(data,ensure_ascii=False,allow_nan=False)))
            return dict(event=event,history=rows(db,event))
    finally:
        db.close()


def export_csv(record):
    out=io.StringIO(newline="")
    writer=csv.writer(out)
    writer.writerow(("event_id","sequence_number","timestamp_utc","action","data_json"))
    for row in record["history"]:
        writer.writerow((row["event"],row["seq"],row["stamp"],row["kind"],json.dumps(row["data"],ensure_ascii=False)))
    return out.getvalue()
