zendesk-cli
===========

CLI utility to interface with the Zendesk API. Based on a query, it will dump, delete, or mark tickets as spam.

Zendesk's query language reference: https://support.zendesk.com/hc/en-us/articles/203663226


Usage
-----

.. code-block:: bash

   zendesk.py -h


Dumping
~~~~~~

.. code-block:: bash

   zendesk.py -a https://yourprefix.zendesk.com/api/v2/ -u you@domain.com/token -f 'tags:trash status:new'


Deleting
~~~~~~~

.. code-block:: bash

   zendesk.py -a https://yourprefix.zendesk.com/api/v2/ -u you@domain.com/token -d 'tags:trash status:new'


Mark as spam
~~~~~~~~~~~

.. code-block:: bash

   zendesk.py -a https://yourprefix.zendesk.com/api/v2/ -u you@domain.com/token -s 'tags:trash status:new'
