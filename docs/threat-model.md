# Threat model and lab boundary

This lab models **observable symptoms**, not attack mechanics. A synthetic event stream can illustrate why a defensive system might alert on bursts, repeated pairing failures, or rapid session turnover. It cannot and must not be used to infer that a real device was contacted.

| In scope | Explicitly out of scope |
|---|---|
| Reproducible mock events | Bluetooth discovery or pairing |
| Risk scoring for classroom discussion | Packet generation or injection |
| Defensive controls and audit concepts | Radio jamming or interference |
| Local browser/API demonstration | Real addresses, MACs, or targets |

The safe boundary is enforced in code by using only generated `SIM-####` identifiers, loopback HTTP, and Python standard-library primitives. The API rejects unknown scenarios and does not expose an input for a device address, adapter, interface, packet size, or thread count.
