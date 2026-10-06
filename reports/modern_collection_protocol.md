# Modern traffic collection protocol and project deadlines

Target completion: December 5, 2026. Core deliverable: reproducible VPN application
category generalization, with Tor as a separate secondary study.

## Minimum feasible collection

Use an owned computer and one fixed VPN provider/endpoint. Start with OpenVPN UDP
if available: the historical VPN dataset used it. Record any protocol difference;
WireGuard alone would combine protocol and temporal shifts.
[Historical VPN setup](https://www.unb.ca/cic/datasets/vpn.html).

Collect browsing, streaming, and file transfer. Target three paired direct/VPN
workloads per category on each of two days: 36 captures, each 3 minutes (108 minutes
of active capture plus setup). A pilot of one direct/VPN pair comes first. Target
at most 50 MB per capture; stop or lower workload intensity if exceeded, and log
any truncation. Cap the full collection around 2 GB. Record actual completed
sessions rather than treating the target as achieved.

Use a fixed browsing URL list, the same streaming content/resolution, and the same
file/server/size for each pair. Counterbalance direct-first and VPN-first order.
Close unrelated applications; separate workloads, reconnect as needed, and record
VPN connectivity verification. Capture both classes at the physical outbound
interface, avoiding loopback/tunnel-interface inner packets. This choice must be
checked against historical capture conditions. Preserve one PCAP per session and
never infer sessions from rows, IP addresses, or arbitrary chunks.

## Metadata and acceptance checks

Record session_id, pair_id, UTC start/end, collection day, traffic_class,
application_category, application/version, OS/version, device, VPN provider,
protocol, endpoint, capture tool/version, physical interface, workload, capture
path, SHA-256, packet count, size, extractor version/commit, timeout, and notes.
A blank manifest is in `reports/modern_capture_manifest.csv`.

Before scaling collection, verify the pilot has packets, correct transport label,
no accidental tunnel-interface capture, and finite/nonempty extracted features.
Pin the extractor and verify time/rate units and flow rules against historical
features with a small manually checkable packet fixture. Require identical ordered
feature columns and meanings; do not silently fabricate missing historical fields.
If only a validated common feature subset is available, retrain both historical
baselines on that subset and identify it as a new experiment.

## Evaluation

Freeze model parameters and preprocessing using historical training only. Do not
fit imputation/scaling or tune thresholds on modern test data. Report direct/VPN
counts, per-category metrics, confusion matrices, and pair/session-level results.
Treat this as a small controlled exploratory transfer study; device, network,
provider, app and protocol differences prevent isolating time as the sole cause.
If modern data is used for tuning, reserve a separate day/session set for testing.

## Calendar and cutoff

- By October 12: complete pilot and resolve extractor compatibility; ask instructor
  whether the small controlled transfer study meets the temporal requirement.
- By October 19: finish collection or decide that compatibility/provenance prevents
  credible transfer scoring. Also stop chasing historical session metadata if no
  practical recovery route exists; report that limitation.
- By November 2: freeze the main experiments, temporal scores if feasible, and Tor
  baseline analysis. No requirement to integrate a pooled three-class classifier.
- By November 16: complete report draft and figures.
- By November 30: finish reproducibility checks and presentation.
- December 5: final submission, leaving the last week for revisions.

No live traffic capture has been started by this protocol document.
