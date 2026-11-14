# Security

No API credential is intentionally included in this repository. Supply ADS
credentials at runtime through `ADS_API_TOKEN` or `ADS_DEV_KEY`.

An earlier public revision embedded an obfuscated ADS credential. Removing it
from the current branch does not revoke the credential or erase Git history.
The credential owner must rotate it and, if required, perform a separately
reviewed history rewrite.

Please report suspected credential exposure privately to the repository owner.
