from __future__ import annotations
from typing import Dict


class serializeable():
	def _serialize(self):
		pass

def serialize(object: serializeable) -> Dict:
	return object._serialize()
