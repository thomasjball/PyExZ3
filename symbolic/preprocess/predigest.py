#
# Copyright (c) 2011, EPFL (Ecole Politechnique Federale de Lausanne)
# All rights reserved.
#
# Created by Marco Canini, Daniele Venzano, Dejan Kostic, Jennifer Rexford
#
# Updated by Thomas Ball (2014)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   -  Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   -  Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#   -  Neither the names of the contributors, nor their associated universities or
#      organizations may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import ast
import unparse
import os

ord_str = """python_ord = ord # make a backup of Python's ord() function
def se_ord(obj):
	__foo = hasattr(obj, '__ord__')
	if __foo:
		whichBranch(True)
		return obj.__ord__()
	else:
		whichBranch(False)
		return python_ord(obj)
ord = se_ord
"""

# remove And/Or in If conditionals and create explicit control-flow instead

class SplitBoolOpPass1(ast.NodeTransformer):
	def visit_If(self, node):
		while isinstance(node.test, ast.BoolOp):
			new_node = ast.If(test=node.test.values.pop(), body=node.body, orelse=node.orelse)
			if isinstance(node.test.op, ast.And):
				if len(node.test.values) == 1:
					node.test = node.test.values[0]
				node.body = [new_node]
				continue
			else:
				if len(node.test.values) == 1:
					node.test = node.test.values[0]
				node.orelse = [new_node]
		node = self.generic_visit(node) # recursion
		return node

	# To do the above for a while loop is a little trickier.
	# perhaps we whould rewrite a while loop as a separate pass?

# lift all computation out of predicate (replace with local variable)

load_cond = ast.Name(id="__se_cond__", ctx=ast.Load())
store_cond = ast.Name(id="__se_cond__", ctx=ast.Store())

# turn while(E): B into  if (E) { while (true) { B if (!E) break} }
class RewriteWhileLoop(ast.NodeTransformer):
	def __init__(self):
		ast.NodeTransformer.__init__(self)

	def visit_While(self,node):
		node = self.generic_visit(node)
		surround_if = ast.If(test=node.test, body=node, orelse=node.orelse)
		node.test = ast.Expr(True)
		end_if = ast.If(test=node.test, body=ast.Continue, orelse=ast.Break)
		node.body = node.body.append(end_if)
		return [surround_if]

class LiftComputationFromConditionalPass2(ast.NodeTransformer):
	def __init__(self):
		ast.NodeTransformer.__init__(self)

	def worker(self,node):
		node = self.generic_visit(node)
		getSym = ast.Assign(targets=[store_cond], value=node.test)
		extract = ast.Call(func=ast.Name(id='getConcrete', ctx=ast.Load()), 
							args=[load_cond], keywords=[], starargs=None, kwargs=None)
		return (extract, getSym)

	def visit_If(self, node):
		extract, getSym = self.worker(node)
		new_node = ast.If(test=extract, body=node.body, orelse=node.orelse)
		return [ getSym, new_node ]

	def visit_While(self, node):
		# special case: don't extract if this is a While(true)
		extract, getSym = self.worker(node)
		new_node = ast.While(test=extract, body=node.body, orelse=node.orelse)
		return [ getSym, new_node ]

# add code to make the then-else branches explicit (even in the absence of user code)

class BranchIdentifierPass3(ast.NodeTransformer):
	def __init__(self, import_se_dict=True):
		ast.NodeTransformer.__init__(self)
		self.se_dict = import_se_dict

	def visit_If(self, node):
		node = self.generic_visit(node) # recursion
		call_node_true = ast.Expr(value=ast.Call(func=ast.Name(id='whichBranch', ctx=ast.Load()), 
			args=[ast.Name(id='True', ctx=ast.Load()), load_cond], keywords=[], starargs=None, kwargs=None))
		call_node_false = ast.Expr(value=ast.Call(func=ast.Name(id='whichBranch', ctx=ast.Load()), 
			args=[ast.Name(id='False', ctx=ast.Load()), load_cond], keywords=[], starargs=None, kwargs=None))
		new_body = [call_node_true] + node.body
		new_orelse = [call_node_false] + node.orelse
		new_node = ast.If(test=node.test, body=new_body, orelse=new_orelse)
		return ast.copy_location(new_node, node)

	def visit_While(self, node):
		node = self.generic_visit(node) # recursion
		call_node_true = ast.Expr(value=ast.Call(func=ast.Name(id='whichBranch', ctx=ast.Load()), 
			args=[ast.Name(id='True', ctx=ast.Load()), load_cond], keywords=[], starargs=None, kwargs=None))
		call_node_false = ast.Expr(value=ast.Call(func=ast.Name(id='whichBranch', ctx=ast.Load()), 
			args=[ast.Name(id='False', ctx=ast.Load()), load_cond], keywords=[], starargs=None, kwargs=None))
		new_body = [call_node_true] + node.body
		new_orelse = [call_node_false] + node.orelse
		new_node = ast.While(test=node.test, body=new_body, orelse=new_orelse)
		return ast.copy_location(new_node, node)

	def visit_Module(self, node):
		""" Add the imports needed to run symbolically """
		node = self.generic_visit(node)
		if self.se_dict:
			import_se_dict = ast.ImportFrom(module="se_dict", names=[ast.alias(name="SeDict", asname=None)], level=0)
		import_instrumentation = ast.ImportFrom(module="symbolic.instrumentation", names=[ast.alias(name="whichBranch", asname=None)], level=0)
		import_extract = ast.ImportFrom(module="symbolic.symbolic_types", names=[ast.alias(name="getConcrete", asname=None)], level=0)

		ord_function = ast.parse(ord_str).body
		#if self.se_dict:
		#	node.body = [import_se_dict,import_instrumentation,import_extract] + ord_function + node.body
		#else:
		node.body = [import_instrumentation,import_extract] + ord_function + node.body
		return node

	def visit_Dict(self, node):
		return ast.Call(func=ast.Name(id='SeDict', ctx=ast.Load()), args=[node], keywords=[], starargs=None, kwargs=None)

def instrumentModule(module_filename, out_dir, is_app=False, in_dir=""):

	mod_file = os.path.join(out_dir, module_filename)

	if os.path.exists(mod_file) and os.stat(os.path.join(in_dir, module_filename)).st_mtime < os.stat(mod_file).st_mtime:
		return

	print "Instrumenting %s" % module_filename

	if "se_dict.py" in module_filename:
		import_se_dict = False
	else:
		import_se_dict = True

	module_contents = file(os.path.join(in_dir, module_filename), "U").read()

	if len(module_contents.strip()) == 0:
		file(mod_file, "w").close()
		return
	root_node = ast.parse(module_contents)
	SplitBoolOpPass1().visit(root_node)
	LiftComputationFromConditionalPass2().visit(root_node)
	BranchIdentifierPass3(import_se_dict).visit(root_node)
	ast.fix_missing_locations(root_node)
	compile(root_node, module_filename, 'exec') # to make sure the new AST is ok
	unparse.Unparser(root_node, file(mod_file, "w"))

def instrumentPackage(package_dir, out_dir, in_dir=""):
	abs_package_dir = os.path.join(in_dir, package_dir)
	for f in os.listdir(abs_package_dir):
		in_f = os.path.join(package_dir, f)
		abs_in_f = os.path.join(in_dir, in_f)
		if f == ".svn" or os.path.splitext(f)[1] == ".pyc" or f[0] == ".":
			continue
		if os.path.isdir(abs_in_f):
			instrumentPackage(in_f, out_dir, in_dir)
		if os.path.isfile(abs_in_f):
			instrumentModule(in_f, out_dir, in_dir=in_dir)

