0.1.9
---
- fixed a nonetype error where empty serverca was passed.

0.1.6
---
- added some exceptions


0.1.5
---
- added option to load cert data directly from memory by creating temp cert files, loading the ssl context and deleting them
- now ssl context creation happens only once.

0.1.2
---
- issue with passing clientname on init