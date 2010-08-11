import re, sys
from string import maketrans

Operators = {
	# Numerator operators
	'Ssssss' : {
		'ss' : '+',
		'sssssssss' : '-',
		'sssss' : '*',
		'sss' : '/',
		'ssssss' : '%',
	},
	# Program Control
	'Sssssss' : {
		'ssssssssss' : 'ifzero',
		'ssssss' : 'ifpos',
		'ssssssss' : 'ifneg',
		'sssssssss' : 'label',
		'sssssssssssssssss' : 'goto',
	},
	# Stack operations
	'Ssssssss' : {
		'sssss' : 'discard',
		'sss' : 'swap',
		'ssssssssssss' : 'duplicate',
	},
	# Output
	'Sssssssss' : {
		'sss' : 'charOut',
		'ssss' : 'numOut',
	},
	# Value
	'Ssssssssss' : 'value'
}

class Slither:
	def __init__(self, input=None):
		self.tokens = []
		self.stack = []
		if input:
			self.input = input
		else:
			self.input = []
	def tokenize(self, input):
		for line in input:
			
			if line.startswith('#'):
				continue
			ops = re.split('[^\S]+', line)

			# Remove blank strings
			ops = [op for op in ops if op]
			
			for op in ops:
				parse_list = re.split('\W+', op)
				identifier = parse_list[0]
				
				if identifier in Operators:
					prefix = Operators[identifier]
					subop = parse_list[1]
					
					if prefix == 'value':
						self.tokens.append(int(subop.translate(maketrans('sS', '01')), 2))
					elif subop in prefix:
						sub_id = prefix[subop]
						if sub_id == 'label' or sub_id == 'goto' or sub_id.startswith('if'):
							sub_id += '-' + ops[1]
						self.tokens.append(sub_id)
	def run(self):
		print self.parse(self.input)

	def parse(self, input):
		if not input:
			return
		
		if isinstance(input, str):
			input = [input]
			
		self.tokenize(input)
		i = 0
		output = ''
		
		while i < len(self.tokens):
			item = self.tokens[i]
			if not isinstance(item, str):
				try:
					self.stack.append(int(item))
				except KeyError:
					self.stack.append(0)
			elif item in '+-*/%':
				self.stack.append(self.operation(self.stack, item))
			elif item.startswith('label'):
				pass
			elif item.startswith('goto'):
				label = re.split('\W+', item)[1]
				i = self.tokens.index('label-' + label)
			elif item == 'charOut':
				output += chr(self.stack.pop())
			elif item == 'numOut':
				x = self.stack.pop()
				output += str(x)
			elif item == 'duplicate':
				first = self.stack.pop()
				self.stack.append(first)
				self.stack.append(first)
			elif item == 'swap':
				first = self.stack.pop()
				second = self.stack.pop()
				self.stack.append(first)
				self.stack.append(second)
			elif item == 'discard':
				self.stack.pop()
			elif item.startswith('ifzero'):
				first = self.stack.pop()
				if first == 0:
					label = re.split('\W+', item)[1]
					i = self.tokens.index('label-' + label)
			elif item.startswith('ifpos'):
				first = self.stack.pop()
				if first > 0:
					label = re.split('\W+', item)[1]
					i = self.tokens.index('label-' + label)
			elif item.startswith('ifneg'):
				first = self.stack.pop()
				if first < 0:
					label = re.split('\W+', item)[1]
					i = self.tokens.index('label-' + label)
			else:
				pass
			i += 1
		self.tokens = []
		if output:
			return output
		else:
			if self.stack:
				return self.stack[-1]
			else:
				return None
	
	def operation(self, stack, op):
		first = stack.pop()
		second = stack.pop()
		return eval(str(second) + op + str(first))

if __name__ == '__main__':
	if len(sys.argv) == 2:
		try:
			file = open(sys.argv[1])
		except IOError:
			print 'File %s cannot be found' % sys.argv[0]
			sys.exit()
		snake = Slither(file)
		snake.run()
