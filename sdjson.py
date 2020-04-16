#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  sdjson.py
#  Scroll down for license info
"""
JSON encoder utilising functools.singledispatch to support custom encoders
for both Python's built-in classes and user-created classes, without as much legwork.


Creating and registering a custom encoder is as easy as:

>>> import sdjson
>>>
>>> @sdjson.dump.register(MyClass)
>>> def encode_myclass(obj):
...     return dict(obj)
>>>

In this case, `MyClass` can be made JSON-serializable simply by calling
:class:`dict <python:dict>` on it. If your class requires more complicated logic
to make it JSON-serializable, do that here.

Then, to dump the object to a string:

>>> class_instance = MyClass()
>>> print(sdjson.dumps(class_instance))
'{"menu": ["egg and bacon", "egg sausage and bacon", "egg and spam", "egg bacon and spam"],
"today\'s special": "Lobster Thermidor au Crevette with a Mornay sauce served in a Provencale
manner with shallots and aubergines garnished with truffle pate, brandy and with a fried egg
on top and spam."}'
>>>

Or to dump to a file:

>>> with open("spam.json", "w") as fp:
...     sdjson.dumps(class_instance, fp)
...
>>>

`sdjson` also provides access to :func:`load <python:json.load>`,
:func:`loads <python:json.loads>`, :class:`~python:json.JSONDecoder`,
:class:`~python:json.JSONDecodeError`, and :class:`~python:json.JSONEncoder`
from the :mod:`~python:json` module, allowing you to use ``sdjson`` as a drop-in replacement
for :mod:`~python:json`.

If you wish to dump an object without using the custom encoders, you can pass
a different :class:`~python:json.JSONEncoder` subclass, or indeed
:class:`~python:json.JSONEncoder` itself to get the stock functionality.

>>> sdjson.dumps(class_instance, cls=sdjson.JSONEncoder)
>>>

TODO: This module does not currently support custom decoders, but might in the future.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Based on https://treyhunner.com/2013/09/singledispatch-json-serializer/
#  Copyright © 2013 Trey Hunner
#  He said "Feel free to use it however you like." So I have.
#
#  Also based on the `json` module (version 2.0.9) by Bob Ippolito from Python 3.7
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com . All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives . All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum . All rights reserved.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#


__all__ = ["load", "loads", "JSONDecoder", "JSONDecodeError", "JSONEncoder", "dump", "dumps"]

__author__ = "Dominic Davis-Foster"
__copyright__ = "2020 Dominic Davis-Foster"

__license__ = "LGPL3+"
__version__ = "0.0.2"
__email__ = "dominic@davis-foster.co.uk"

# stdlib
import json
from functools import singledispatch

# 3rd party
from domdf_python_tools.doctools import is_documented_by, append_docstring_from, make_sphinx_links


def sphinxify_json_docstring():
	"""
	Turn references in the docstring to :class:`~python:json.JSONEncoder` into proper links.
	"""
	
	def wrapper(target):
		# To save having the `sphinxify_docstring` decorator too
		target.__doc__ = make_sphinx_links(target.__doc__)
		
		target.__doc__ = target.__doc__.replace("``JSONEncoder``", ":class:`~python:json.JSONEncoder`")
		target.__doc__ = target.__doc__.replace("``.default()``", ":meth:`~python:json.JSONEncoder.default`")

		return target
	
	return wrapper


@singledispatch
@sphinxify_json_docstring()
@append_docstring_from(json.dump)
def dump(obj, fp, **kwargs):
	"""
	Serialize custom Python classes to JSON.
	Custom classes can be registered using the ``@dump.register(<type>)`` decorator.
	"""
	
	iterable = json.dumps(obj, **kwargs)
	
	for chunk in iterable:
		fp.write(chunk)


@sphinxify_json_docstring()
@append_docstring_from(json.dumps)
def dumps(
		obj, *, skipkeys=False, ensure_ascii=True, check_circular=True,
		allow_nan=True, cls=None, indent=None, separators=None,
		default=None, sort_keys=False, **kw,
		):
	"""
	Serialize custom Python classes to JSON.
	Custom classes can be registered using the ``@dump.register(<type>)`` decorator.
	"""
	
	if (
			not skipkeys and ensure_ascii
			and check_circular and allow_nan
			and cls is None and indent is None
			and separators is None and default is None
			and not sort_keys and not kw):
		return _default_encoder.encode(obj)
	if cls is None:
		cls = _CustomEncoder
	return cls(
			skipkeys=skipkeys, ensure_ascii=ensure_ascii,
			check_circular=check_circular, allow_nan=allow_nan, indent=indent,
			separators=separators, default=default, sort_keys=sort_keys,
			**kw).encode(obj)


# Provide access to remaining objects from json module.
# We have to do it this way to sort out the docstrings for sphinx without
#  modifying the original docstrings.
@sphinxify_json_docstring()
@append_docstring_from(json.load)
def load(*args, **kwargs):
	"""
	This is just the :func:`load <python:json.load>` function from Python's :mod:`~python:json` module.
	"""
	return json.load(*args, **kwargs)


@sphinxify_json_docstring()
@append_docstring_from(json.loads)
def loads(*args, **kwargs):
	"""
	This is just the :func:`loads <python:json.loads>` function from Python's :mod:`~python:json` module.
	"""
	return json.loads(*args, **kwargs)


@sphinxify_json_docstring()
@append_docstring_from(json.JSONEncoder)
class JSONEncoder(json.JSONEncoder):
	"""
	This is just the :class:`~python:json.JSONEncoder` class from Python's :mod:`~python:json` module.
	"""
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
	@sphinxify_json_docstring()
	@is_documented_by(json.JSONEncoder.default)
	def default(self, o):
		return super().default(o)
		
	@sphinxify_json_docstring()
	@is_documented_by(json.JSONEncoder.encode)
	def encode(self, o):
		return super().encode(o)
	
	@sphinxify_json_docstring()
	@is_documented_by(json.JSONEncoder.iterencode)
	def iterencode(self, o):
		return super().iterencode(o)
	
	
@sphinxify_json_docstring()
@append_docstring_from(json.JSONDecoder)
class JSONDecoder(json.JSONDecoder):
	"""
	This is just the :class:`~python:json.JSONEncoder` class from Python's :mod:`~python:json` module.
	"""
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
	@sphinxify_json_docstring()
	@is_documented_by(json.JSONDecoder.decode)
	def decode(self, *args, **kwargs):
		return super().decode(*args, **kwargs)
		
	@sphinxify_json_docstring()
	@is_documented_by(json.JSONDecoder.raw_decode)
	def raw_decode(self, *args, **kwargs):
		return super().raw_decode(*args, **kwargs)
		
		
@sphinxify_json_docstring()
@append_docstring_from(json.JSONDecodeError)
class JSONDecodeError(json.JSONDecodeError):
	"""
	This is just the :class:`~python:json.JSONEncoder` class from Python's :mod:`~python:json` module.
	"""


# Custom encoder for sdjson
class _CustomEncoder(JSONEncoder):
	def default(self, o):
		for type_, handler in dump.registry.items():
			if isinstance(o, type_) and type_ is not object:
				return handler(o)
		return super().default(o)


_default_encoder = _CustomEncoder(
		skipkeys=False,
		ensure_ascii=True,
		check_circular=True,
		allow_nan=True,
		indent=None,
		separators=None,
		default=None,
		)
