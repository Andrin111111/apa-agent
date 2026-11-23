"""Erkennung v2: jede neue Regel feuert, Grenzfaelle knapp darunter nicht, Ketten nach Prioritaet."""
import unittest
from datetime import datetime

import _util  # noqa: F401
from detect_v2 import evaluate

NOW = datetime(2026, 5, 20, 18, 0)
BASE = {"order_value": "1000", "open_items": "0", "credit_limit": "50000", "payment_terms_days": "30",
        "promised_delivery_date": "2026-06-30", "restock_date": "", "invoice_amount": "0",
        "credit_note_amount": "0", "paid_amount": "0", "free_text": ""}


def case(**kw):
    return dict(BASE, **{k: str(v) for k, v in kw.items()})


def evs(*pairs):
    return [{"activity": a, "timestamp": datetime.fromisoformat(t)} for a, t in pairs]


SHIPPED = [("Auftrag erfassen", "2026-04-01 09:00"), ("Versenden", "2026-04-03 10:00")]
INVOICED = SHIPPED + [("Rechnung stellen", "2026-05-10 10:00")]


class TestDetectV2(unittest.TestCase):
    def trig(self, c, ev, now=NOW):
        return evaluate(c, evs(*ev), now)

    def test_happy_path_none(self):
        r = self.trig(case(invoice_amount=1000, paid_amount=1000), INVOICED + [("Zahlungseingang", "2026-05-15 10:00")])
        self.assertEqual(r["hard_triggers"], [])
        self.assertEqual(r["detected_type"], "none")

    def test_e8_storno_after_ship(self):
        r = self.trig(case(), SHIPPED + [("Auftrag stornieren", "2026-04-05 10:00")])
        self.assertEqual(r["detected_type"], "E8")

    def test_storno_before_ship_no_e3_no_e8(self):
        ev = [("Auftrag erfassen", "2026-05-01 09:00"), ("Auftrag stornieren", "2026-05-02 09:00")]
        r = self.trig(case(promised_delivery_date="2026-05-10"), ev)   # Termin verstrichen
        self.assertEqual(r["hard_triggers"], [])

    def test_e9_price_deviation_and_tolerance(self):
        self.assertEqual(self.trig(case(invoice_amount=1002), INVOICED)["detected_type"], "E9")
        self.assertEqual(self.trig(case(invoice_amount=998), INVOICED)["detected_type"], "E9")
        self.assertEqual(self.trig(case(invoice_amount=1001), INVOICED)["hard_triggers"], [])

    def test_e10_underpayment_respects_credit_note(self):
        paid = INVOICED + [("Zahlungseingang", "2026-05-15 10:00")]
        self.assertEqual(self.trig(case(invoice_amount=1000, paid_amount=700), paid)["detected_type"], "E10")
        self.assertEqual(self.trig(case(invoice_amount=1000, paid_amount=999), paid)["hard_triggers"], [])
        r = self.trig(case(invoice_amount=1000, credit_note_amount=300, paid_amount=700), paid)
        self.assertEqual(r["hard_triggers"], [])

    def test_e11_return_without_credit_note(self):
        ret = SHIPPED + [("Reklamation erfassen", "2026-04-20 10:00"), ("Retoure erfassen", "2026-05-09 10:00")]
        self.assertEqual(self.trig(case(), ret)["detected_type"], "E11")                       # 11 Tage
        self.assertEqual(self.trig(case(), ret, datetime(2026, 5, 19, 18))["hard_triggers"], [])   # genau 10
        credited = ret + [("Gutschrift erstellen", "2026-05-12 10:00")]
        self.assertEqual(self.trig(case(), credited)["hard_triggers"], [])

    def test_e12_backorder_and_boundary(self):
        ev = [("Auftrag erfassen", "2026-05-15 09:00"), ("Ware nachbestellen", "2026-05-15 11:00")]
        c = case(promised_delivery_date="2026-05-28", restock_date="2026-05-28")
        self.assertEqual(self.trig(c, ev)["detected_type"], "E12")
        c = case(promised_delivery_date="2026-05-28", restock_date="2026-05-27")
        self.assertEqual(self.trig(c, ev)["hard_triggers"], [])

    def test_e3_wins_over_e12(self):
        ev = [("Auftrag erfassen", "2026-05-15 09:00"), ("Ware nachbestellen", "2026-05-15 11:00")]
        r = self.trig(case(promised_delivery_date="2026-05-21", restock_date="2026-05-25"), ev)
        self.assertEqual(set(r["hard_triggers"]), {"E3", "E12"})
        self.assertEqual(r["detected_type"], "E3")

    def test_chains_pick_root_cause_over_e6(self):
        late = datetime(2026, 6, 30, 18)                                   # Rechnung 10.05. + 30 Tage ueberfaellig
        r = self.trig(case(invoice_amount=1100), INVOICED, late)
        self.assertEqual((set(r["hard_triggers"]), r["detected_type"]), ({"E6", "E9"}, "E9"))
        ret = INVOICED + [("Reklamation erfassen", "2026-05-12 10:00"), ("Retoure erfassen", "2026-05-13 10:00")]
        r = self.trig(case(invoice_amount=1000), ret, late)
        self.assertEqual((set(r["hard_triggers"]), r["detected_type"]), ({"E6", "E11"}, "E11"))
        st = INVOICED + [("Auftrag stornieren", "2026-05-12 10:00")]
        r = self.trig(case(invoice_amount=1000), st, late)
        self.assertEqual((set(r["hard_triggers"]), r["detected_type"]), ({"E6", "E8"}, "E8"))

    def test_events_after_now_ignored(self):
        r = self.trig(case(), SHIPPED + [("Auftrag stornieren", "2026-05-21 10:00")])
        self.assertEqual(r["hard_triggers"], [])


if __name__ == "__main__":
    unittest.main()
