import json

from . import ast
from .utils import gen_uid

def serialise_statement(sprite, statement):
	if not issubclass(type(statement), ast.Statement):
		raise Exception(f"Cannot serialise {statement!r} as a statement")

	blocks_json = sprite.blocks_json

	uid = gen_uid()
	blocks_json[uid] = {
		"inputs": {},
		"fields": {},
		"shadow": False,
		"topLevel": False,
	}
	
	# ===== EVENTS =======
	if statement.op == "event_whenflagclicked":
		out = {
			"opcode": "event_whenflagclicked"
		}
	
	elif statement.op == "event_whenkeypressed":
		out = {
			"opcode": "event_whenkeypressed",
			"fields": {
				"KEY_OPTION": [statement.args["KEY_OPTION"], None],
			}
		}
	
	# ===== CONTROL =======
	elif statement.op == "control_repeat":
		out = {
			"opcode": "control_repeat",
			"inputs": {
				"TIMES": sprite.serialise_arg(statement.args["TIMES"], uid),
				"SUBSTACK": sprite.serialise_script(statement.args["SUBSTACK"], uid)
			}
		}
	elif statement.op == "control_repeat_until":
		out = {
			"opcode": "control_repeat_until",
			"inputs": {
				"CONDITION": sprite.serialise_bool(statement.args["CONDITION"], uid),
				"SUBSTACK": sprite.serialise_script(statement.args["SUBSTACK"], uid)
			}
		}
	elif statement.op == "control_forever":
		out = {
			"opcode": "control_forever",
			"inputs": {
				"SUBSTACK": sprite.serialise_script(statement.args["SUBSTACK"], uid)
			}
		}
	elif statement.op == "control_if":
		out = {
			"opcode": "control_if",
			"inputs": {
				"CONDITION": sprite.serialise_bool(statement.args["CONDITION"], uid),
				"SUBSTACK": sprite.serialise_script(statement.args["SUBSTACK"], uid)
			}
		}
	elif statement.op == "control_if_else":
		out = {
			"opcode": "control_if_else",
			"inputs": {
				"CONDITION": sprite.serialise_bool(statement.args["CONDITION"], uid),
				"SUBSTACK": sprite.serialise_script(statement.args["SUBSTACK"], uid),
				"SUBSTACK2": sprite.serialise_script(statement.args["SUBSTACK2"], uid)
			}
		}
	elif statement.op == "control_wait":
		out = {
			"opcode": "control_wait",
			"inputs": {
				"DURATION": sprite.serialise_arg(statement.args["DURATION"], uid)
			}
		}
	
	# ===== DATA =======
	elif statement.op == "data_setvariableto":
		out = {
			"opcode": "data_setvariableto",
			"inputs": {
				"VALUE": sprite.serialise_arg(statement.args["VALUE"], uid)
			},
			"fields": {
				"VARIABLE": [
					statement.args["VARIABLE"].name,
					statement.args["VARIABLE"].uid
				]
			}
		}
	elif statement.op == "data_changevariableby":
		out = {
			"opcode": "data_changevariableby",
			"inputs": {
				"VALUE": sprite.serialise_arg(statement.args["VALUE"], uid)
			},
			"fields": {
				"VARIABLE": [
					statement.args["VARIABLE"].name,
					statement.args["VARIABLE"].uid
				]
			}
		}
	elif statement.op == "data_replaceitemoflist":
		out = {
			"opcode": "data_replaceitemoflist",
			"inputs": {
				"INDEX": sprite.serialise_arg(statement.args["INDEX"], uid),
				"ITEM": sprite.serialise_arg(statement.args["ITEM"], uid)
			},
			"fields": {
				"LIST": [
					statement.args["LIST"].name,
					statement.args["LIST"].uid
				]
			}
		}
	elif statement.op == "data_addtolist":
		out = {
			"opcode": "data_addtolist",
			"inputs": {
				"ITEM": sprite.serialise_arg(statement.args["ITEM"], uid)
			},
			"fields": {
				"LIST": [
					statement.args["LIST"].name,
					statement.args["LIST"].uid
				]
			}
		}
	elif statement.op == "data_deletealloflist":
		out = {
			"opcode": "data_deletealloflist",
			"fields": {
				"LIST": [
					statement.args["LIST"].name,
					statement.args["LIST"].uid
				]
			}
		}
	elif statement.op == "data_deleteoflist":
		out = {
			"opcode": "data_deleteoflist",
			"inputs": {
				"INDEX": sprite.serialise_arg(statement.args["INDEX"], uid)
			},
			"fields": {
				"LIST": [
					statement.args["LIST"].name,
					statement.args["LIST"].uid
				]
			}
		}
	
	# ======= custom blocks =======

	elif statement.op == "procedures_definition":
		out = {
			"opcode": "procedures_definition",
			"inputs": {
				"custom_block": sprite.serialise_procproto(statement.proto, uid)
			}
		}

	elif statement.op == "procedures_call":
		inputs = {}
		for arg, var in zip(statement.args["ARGS"], statement.proc.vars):
			inputs[var.uid2] = sprite.serialise_arg(arg, uid)
		out = {
			"opcode": "procedures_call",
			"inputs": inputs,
			"mutation": {
				"tagName": "mutation",
				"children": [],
				"proccode": statement.proc.proccode,
				"argumentids": json.dumps(list(inputs.keys())),
				"warp": "true" if statement.proc.turbo else "false"
			}
		}

	elif statement.op == "sensing_askandwait":
		out = {
			"opcode": "sensing_askandwait",
			"inputs": {
				"QUESTION": sprite.serialise_arg(statement.prompt, uid)
			}
		}

	# ======= motion =======

	elif statement.op == "motion_gotoxy":
		out = {
			"opcode": statement.op,
			"inputs": {
				"X": sprite.serialise_arg(statement.args["X"], uid),
				"Y": sprite.serialise_arg(statement.args["Y"], uid)
			}
		}
	
	elif statement.op == "motion_changexby":
		out = {
			"opcode": statement.op,
			"inputs": {
				"DX": sprite.serialise_arg(statement.args["DX"], uid)
			}
		}
	
	elif statement.op == "motion_setx":
		out = {
			"opcode": statement.op,
			"inputs": {
				"X": sprite.serialise_arg(statement.args["X"], uid)
			}
		}
	
	elif statement.op == "motion_changeyby":
		out = {
			"opcode": statement.op,
			"inputs": {
				"DY": sprite.serialise_arg(statement.args["DY"], uid)
			}
		}
	
	elif statement.op == "motion_sety":
		out = {
			"opcode": statement.op,
			"inputs": {
				"Y": sprite.serialise_arg(statement.args["Y"], uid)
			}
		}

	# ======= looks =======

	elif statement.op in ["looks_show", "looks_hide"]:
		out = {
			"opcode": statement.op,
			"inputs": {}
		}
	
	elif statement.op == "looks_switchcostumeto":
		out = {
			"opcode": statement.op,
			"inputs": {
				"COSTUME": sprite.serialise_arg(statement.args["COSTUME"], uid)
			}
		}

	# TODO: set effect

	# ======= pen =======

	elif statement.op in ["pen_clear", "pen_stamp", "pen_penDown", "pen_penUp"]:
		out = {"opcode": statement.op}

	elif statement.op == "pen_setPenColorToColor":
		out = {
			"opcode": "pen_setPenColorToColor",
			"inputs": {
				"COLOR": sprite.serialise_arg(statement.args["COLOR"], uid, alternative=[9, "#FF0000"])
			}
		}
	
	elif statement.op == "pen_setPenSizeTo":
		out = {
			"opcode": "pen_setPenSizeTo",
			"inputs": {
				"SIZE": sprite.serialise_arg(statement.args["SIZE"], uid)
			}
		}

	else:
		raise Exception(f"I don't know how to serialise this op: {statement.op!r}")

	blocks_json[uid].update(out)
	return uid
