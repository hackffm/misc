#!/usr/bin/python
"""
Create SVG image files with python.
"""
units="mm"
try:
	from style import style # should be in working directory
except ImportError:
	class StylePlaceholder:
		def __getitem__(self, key):
			raise Exception("no style.py found - only inline styles possible")
	style=StylePlaceholder()

def class_or_style(name,useStylesheet):
	if name is None:
		return ""
	return 'class="{}"'.format(name) if useStylesheet else 'style="{}"'.format(style[name])

class Text():
	"""Renders a <text></text> tag"""
	def __init__(self,pos,text,styleclass,**kwargs):
		self.styleclass = styleclass
		self.pos=pos
		self.text=text
		self.params=kwargs
	def get_svg(self,useStylesheet):
		 return '<text x="{}" y="{}" {style} {}>{}</text>'.format(self.pos[0],self.pos[1]," ".join(['{}="{}"'.format(k,v) for k, v in self.params.iteritems()]),self.text, style=class_or_style(self.styleclass,useStylesheet))


class Group():
	"""Renders a <g></g> tag."""
	def __init__(self,transformation=None):
		self.params={}
		self.objects=[]
		if transformation is not None:
			self.params["transform"]="translate({},{})".format(transformation[0],transformation[1])
	
	def get_svg(self,useStylesheet):
		svg="<g {}>\n".format(" ".join(["{}=\"{}\"".format(k,v) for k,v in self.params.iteritems()]))
		for i in range(len(self.objects)):
			svg+=self.objects[i].get_svg(useStylesheet)+"\n"
		svg+="</g>\n"
		return svg

class Line():
	"""A simple path consisting of linear connections between points."""
	def __init__(self,styleclass,points,connect_to_start=False):
		self.styleclass=styleclass
		self.points=points
		self.connect_to_start=connect_to_start
	def get_svg(self,useStylesheet):
		string="M"
		for point in self.points:
			string+=" {},{}".format(point[0],point[1])
		if self.connect_to_start:
			string+=" z"
		return "<path {style} d=\"{}\" />".format(string, style=class_or_style(self.styleclass,useStylesheet))

class PathVertex():
	pass

class PathMove(PathVertex):
	def __init__(self,x,y):
		self.x=x
		self.y=y
	def get(self):
		return "M {} {}".format(self.x,self.y)

class PathLine(PathVertex):
	def __init__(self,x,y):
		self.x=x
		self.y=y
	def get(self):
		return "L {} {}".format(self.x,self.y)

class PathArc(PathVertex):
	def __init__(self,x,y,rx,ry,rot=0,large=False,sweep=False):
		self.x=x
		self.y=y
		self.rx=rx
		self.ry=ry
		self.rot=rot
		self.large=large
		self.sweep=sweep
	def get(self):
		return "A {},{} {} {} {} {},{}".format(self.rx,self.ry,self.rot, 1 if self.large else 0, 1 if self.sweep else 0,self.x,self.y)

m=PathMove
l=PathLine
a=PathArc

class Path():
	"""A more complex path consisting of moves, lines and arcs."""
	def __init__(self,styleclass, vertices, closed=False):
		self.styleclass=styleclass
		for v in vertices:
			assert isinstance(v,PathVertex)
		self.vertices=vertices
		for v in vertices:
			print(v.get())
		self.closed=closed
	
	def get_svg(self,useStylesheet):
		return "<path {style} d=\"{}\" />".format(" ".join([v.get() for v in self.vertices])+(" z" if self.closed else ""), style=class_or_style(self.styleclass,useStylesheet))

class Rectangle():
	def __init__(self,styleclass,position,size):
		self.styleclass=styleclass
		self.position=position
		self.size=size
	def get_svg(self,useStylesheet):
		return "<rect {style} width=\"{}\" height=\"{}\" x=\"{}\" y=\"{}\" />\n".format(self.size[0],self.size[1],self.position[0],self.position[1], style=class_or_style(self.styleclass,useStylesheet))

class Circle():
	def __init__(self,styleclass,position,radius):
		self.styleclass=styleclass
		self.position=position
		self.radius=radius
	def get_svg(self,useStylesheet):
		return "<circle {style} cx=\"{}\" cy=\"{}\" r=\"{}\" />\n".format(self.position[0],self.position[1],self.radius, style=class_or_style(self.styleclass,useStylesheet))

class SVG():
	def __init__(self,dimensions,svgid,preamble="",stylesheet=None):
		self.stylesheet = stylesheet
		self.dimensions=dimensions
		self.svgid=svgid
		self.children=[]
		self.preamble = preamble
	def get_svg(self):
		string ="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
		string+=self.preamble
		if self.stylesheet is not None:
			string+='<?xml-stylesheet href="{}" type="text/css"?>'.format(self.stylesheet)
		string+="<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:inkscape=\"http://www.inkscape.org/namespaces/inkscape\""
		string+=" width=\"{width}{units}\" height=\"{height}{units}\" viewBox=\"{viewBox}\" id=\"{id}\" version=\"1.1\">\n".format(
			width=self.dimensions[0], height=self.dimensions[1],
			id=self.svgid,units=units, viewBox="0 0 {} {}".format(self.dimensions[0], self.dimensions[1]))
		for i in range(len(self.children)):
			string+=self.children[i].get_svg(self.stylesheet is not None)
		string+="</svg>\n";
		return string

if __name__=="__main__":
	style={"cut":"fill:none;stroke:#000000","engrave":"fill:#000000;fill-opacity:1;fill-rule:evenodd;stroke:none"}
	svg=SVG((150,100),"board")
	svg.children.append(Line("cut",[(10,20),(20,10),(50,10),(60,20),(80,20),(90,10),(120,10),(130,20)]))
	svg.children.append(Rectangle("engrave",(20,20),(10,10)))
	with open("test.svg","w") as f:
		f.write(svg.get_svg())
