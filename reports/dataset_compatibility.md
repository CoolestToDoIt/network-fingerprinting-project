# Dataset compatibility audit — October 5, 2026

| Property | VPN Scenario B ARFF | Tor Scenario A CSV | Tor Scenario B CSV |
| --- | --- | --- | --- |
| Raw flows | 18,758 | 84,194 | 14,508 |
| Binary transport label | VPN/direct | Tor/NonTor | absent |
| Application categories | 7, both classes | absent | 8, Tor rows only |
| Native numeric features after endpoint exclusion | 23 | 24 | 24 |
| Filename timeout variant | 15s | 5s | 5s |
| Session IDs | absent | absent | absent |
| Exact duplicate rows | 684 | 493 | 30 |

The revised VPN study removes all exact duplicate rows before splitting, leaving
18,074 flows. There are 743 duplicate numeric feature vectors and 23 unique
feature vectors associated with both transport labels. Identical numeric vectors
are not reliable session identifiers. Exact deduplication does not remove all
flow correlation or prove independence.

An exact join on the 28 non-label columns (endpoints included) finds every one
of the 14,508 Scenario B rows in Scenario A with the label TOR. This establishes
local file overlap; it does not supply NonTor application labels. Do not concatenate
the Tor files or infer application labels by row order.

The official Tor description says its NonTor traffic reuses benign traffic from
the VPN project. Therefore a pooled VPN/Tor study risks cross-dataset train/test
overlap even when filenames differ. A three-class experiment is deferred until
provenance and deduplication across datasets can be established.
[Official Tor dataset description](https://www.unb.ca/cic/datasets/tor.html).

## Feature mapping candidates — not a validated adapter

| VPN | Tor | Compatibility status |
| --- | --- | --- |
| duration | Flow Duration | time units/extractor settings unverified |
| flowBytesPerSecond | Flow Bytes/s | nominal bytes/s; rate implementation unverified |
| flowPktsPerSecond | Flow Packets/s | nominal packets/s; implementation unverified |
| mean/std/min/max_flowiat | Flow IAT Mean/Std/Min/Max | units and direction convention unverified |
| mean/min/max_fiat | Fwd IAT Mean/Min/Max | units and direction convention unverified |
| mean/min/max_biat | Bwd IAT Mean/Min/Max | units and direction convention unverified |
| mean/std/min/max_active | Active Mean/Std/Min/Max | active threshold and units unverified |
| mean/std/min/max_idle | Idle Mean/Std/Min/Max | idle threshold and units unverified |
| total_fiat / total_biat | absent | IAT sums, not packet counts; exclude from any common subset |
| absent | Protocol; directional IAT Std | not shared |

The VPN duration maximum exceeds 600 million in raw units; a 15s filename is not
a guarantee that every flow duration is capped at 15 seconds. Neither field names
nor ranges prove units. Do not automatically divide durations or align timeouts.
Both official pages identify ISCXFlowMeter, but do not pin the export version or
provide a complete unit dictionary. The attempted upstream README lookup failed;
extractor provenance remains open.
[Official VPN dataset description](https://www.unb.ca/cic/datasets/vpn.html).

## Decision

Keep VPN and Tor studies separate. Native numeric features are usable for each
within-dataset baseline. A common feature schema is only a candidate until source
code/definitions and fixture-based extraction verify units, timeout, flow keys,
direction, active/idle thresholds, and missing-value conventions. Modern traffic
must pass that verification before a temporal score is presented. If identical
extraction cannot be established, call the experiment cross-domain exploratory
transfer, with capture/extractor differences explicitly confounded with time.
