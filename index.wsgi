#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import sae

#sys.path.insert(0, os.path.join(os.getcwd(), "virtualenv.bundle"))

from application import create_app
app = create_app()

application = sae.create_wsgi_app(app)
