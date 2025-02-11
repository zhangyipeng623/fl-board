from .urls import router
from .node import node
from .db import db
from .ruler import ruler
from .net import net

router_list = [router, node, db, ruler, net]