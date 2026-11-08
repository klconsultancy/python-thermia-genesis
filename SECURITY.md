# Security policy

## Supported versions

Only the latest release receives security fixes.

## Reporting a vulnerability

Report vulnerabilities privately through [GitHub's private vulnerability reporting](https://github.com/klconsultancy/python-thermia-genesis/security/advisories/new), not in a public issue.

Include what an attacker can do, the steps to reproduce it, and the affected version or commit. You will get an answer within a week. Once a fix is released, the advisory is published with credit to you unless you prefer otherwise.

The library talks Modbus to a Thermia heat pump, which has no authentication of its own. It only reads today, but the pump accepts writes to its settings. Issues that let the library write to a register the caller did not ask for, or that make it misreport the pump's state (an alarm, a temperature), are treated as the most severe.
