#
# Project:
#   glideinWMS
#
# File Version: 
#
# Description: general purpose python expression parser and unparser
#
# Author:
#  Igor Sfiligoi 
#


import string
import compiler

# these are the ast objects currently supported
from ast import Name, List, Tuple, And, Or, Not, Compare, Add, Sub, FloorDiv, Div, Mod, Subscript, Slice, Lambda


# convert an expression string into an ast object
def parse(str):
    # pylint: disable=E1103
    return compiler.pycodegen.Expression(str, '<string>')._get_tree().node
    # pylint: enable=E1103


# convert an ast object into a code object
def compile(obj):
    tmp = compiler.ast.Expression(obj)
    tmp.filename = '<string>'  # needed by the code generator
    return compiler.pycodegen.ExpressionCodeGenerator(tmp).getCode()


# convert an ast object back into a string
def unparse(obj, raise_on_unknown=False):
    if isinstance(obj, Name):
        return "%s" % obj.name
    elif isinstance(obj, List):
        strs = []
        for n in obj.nodes:
            strs.append("%s" % unparse(n, raise_on_unknown))
        return "[%s]" % ",".join(strs)
    elif isinstance(obj, Tuple):
        strs = []
        for n in obj.nodes:
            strs.append("%s" % unparse(n, raise_on_unknown))
        return "(%s)" % ",".join(strs)
    elif isinstance(obj, And):
        strs = []
        for n in obj.nodes:
            strs.append("(%s)" % unparse(n, raise_on_unknown))
        return " and ".join(strs)
    elif isinstance(obj, Or):
        strs = []
        for n in obj.nodes:
            strs.append("(%s)" % unparse(n, raise_on_unknown))
        return " or ".join(strs)
    elif isinstance(obj, Not):
        return "not (%s)" % unparse(obj.expr, raise_on_unknown)
    elif isinstance(obj, Compare):
        if len(obj.ops) == 1:
            op = obj.ops[0]
            return "(%s) %s (%s)" % (unparse(obj.expr, raise_on_unknown), op[0], unparse(op[1], raise_on_unknown))
        else:
            if raise_on_unknown:
                raise ValueError("len(Compare.ops)!=1")
            else:
                return "<unknown op>"
    elif isinstance(obj, Add):
        return "(%s) + (%s)" % (unparse(obj.left, raise_on_unknown), unparse(obj.right, raise_on_unknown))
    elif isinstance(obj, Sub):
        return "(%s) - (%s)" % (unparse(obj.left, raise_on_unknown), unparse(obj.right, raise_on_unknown))
    elif isinstance(obj, Div):
        return "(%s) / (%s)" % (unparse(obj.left, raise_on_unknown), unparse(obj.right, raise_on_unknown))
    elif isinstance(obj, FloorDiv):
        return "(%s) / (%s)" % (unparse(obj.left, raise_on_unknown), unparse(obj.right, raise_on_unknown))
    elif isinstance(obj, Mod):
        return "(%s) / (%s)" % (unparse(obj.left, raise_on_unknown), unparse(obj.right, raise_on_unknown))
    elif isinstance(obj, Subscript):
        if (obj.flags == 'OP_APPLY') and (len(obj.subs) == 1):
            return "%s[%s]" % (unparse(obj.expr, raise_on_unknown), unparse(obj.subs[0], raise_on_unknown))
        else:
            if raise_on_unknown:
                if obj.flags != 'OP_APPLY':
                    raise ValueError("Subscript.flags!='OP_APPLY'")
                else:
                    raise ValueError("len(Subscript.subs)!=1")
            else:
                return "<unknown subsc>"
    elif isinstance(obj, Slice):
        if obj.flags == 'OP_APPLY':
            l = ""
            if obj.lower is not None:
                l = unparse(obj.lower, raise_on_unknown)
            u = ""
            if obj.upper is not None:
                u = unparse(obj.upper, raise_on_unknown)
            return "%s[%s:%s]" % (unparse(obj.expr, raise_on_unknown), l, u)
        else:
            if raise_on_unknown:
                raise ValueError("Slice.flags!='OP_APPLY'")
            else:
                return "<unknown slice>"
    elif isinstance(obj, Lambda):
        if obj.flags == 0:
            astrs = []
            alen = len(obj.argnames)
            dlen = len(obj.defaults)
            for i in range(alen):
                a = obj.argnames[i]
                di = (dlen - alen) + i
                if di >= 0:
                    d = obj.defaults[di]
                    astrs.append("%s=%s" % (a, unparse(d, raise_on_unknown)))
                else:
                    astrs.append(a)
            return "lambda %s:%s" % (",".join(astrs), unparse(obj.code, raise_on_unknown))
        else:
            if raise_on_unknown:
                raise ValueError("Lambda.flags!=0")
            else:
                return "<unknown lambda>"
    else:
        if raise_on_unknown:
            raise TypeError("Unsupported instance type: %s" % repr(obj))
        else:
            return "<unknown>"
