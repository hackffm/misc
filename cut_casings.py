from svg import SVG,Line,Rectangle,Path,m,l,a,Group,Circle
import itertools


default_params=dict(
	margin=3.0,
	material_width=3.0,
	corner_radius=3.0+3.0,
	tongue_margin=5.0,
	tongue_length=10.0,
	screw_radius=2.0
)

class Casing():
	def __init__(self, width, height, z, screw_positions=None, inner_pos=True, **kwargs):
		self.__dict__.update(default_params)
		self.__dict__.update(kwargs)
		self.screw_positions = screw_positions
		
		if inner_pos:
			width+=2*(self.margin+self.material_width)
			height+=2*(self.margin+self.material_width)
			z+=2*self.material_width
		self.width=width
		self.height=height
		self.z=z
	
	def get_tongue_positions(self, length):
		count=int(length/(2*self.tongue_length))
		print(count)
		spacing=float(length - 2*self.tongue_margin - count*self.tongue_length)/(count-1)
		start_positions=[self.tongue_margin+(spacing+self.tongue_length)*float(i) for i in range(count)]
		return [(s,s+self.tongue_length) for s in start_positions]
	
	def top(self):
		outlines=Group()
		
		# outlines
		outlines.objects.append(Path("cut",[
			m(self.corner_radius,0),
			l(self.width-self.corner_radius,0),
			a(self.width,self.corner_radius,self.corner_radius,self.corner_radius,sweep=True),
			l(self.width,self.height-self.corner_radius),
			a(self.width-self.corner_radius, self.height,self.corner_radius,self.corner_radius,sweep=True),
			l(self.corner_radius, self.height),
			a(0,self.height-self.corner_radius, self.corner_radius, self.corner_radius, sweep=True),
			l(0,self.corner_radius),
			a(self.corner_radius, 0, self.corner_radius, self.corner_radius, sweep=True)
		]))
		
		# cuts for side 1+3
		tstart=self.margin+self.material_width
		tpositions=self.get_tongue_positions(self.width-2*tstart)
		for h_pos in [self.margin, self.height-self.margin-self.material_width]:
			for tpos in tpositions:
				outlines.objects.append(Path("cut",[
					m(tstart+tpos[0], h_pos),
					l(tstart+tpos[1], h_pos),
					l(tstart+tpos[1], h_pos+self.material_width),
					l(tstart+tpos[0], h_pos+self.material_width)
				], closed=True))
		
		# cuts for side 2+4
		tpositions=self.get_tongue_positions(self.height-2*tstart)
		for w_pos in [self.margin, self.width-self.margin-self.material_width]:
			for tpos in tpositions:
				outlines.objects.append(Path("cut",[
					m(w_pos, tstart+tpos[0]),
					l(w_pos, tstart+tpos[1]),
					l(w_pos+self.material_width, tstart+tpos[1]),
					l(w_pos+self.material_width, tstart+tpos[0])
				], closed=True))
		
		mar=self.margin+self.material_width+self.screw_radius
		if self.screw_positions is None:
			self.screw_positions=[
				(mar           ,mar),
				(self.width-mar,mar),
				(self.width-mar,self.height-mar),
				(mar           ,self.height-mar)
			]
		for p in self.screw_positions:
			outlines.objects.append(Circle("cut",p,self.screw_radius))
		
		return (outlines,Group(transformation=(self.margin+self.material_width,self.margin+self.material_width)))
	
	def make_tongues(self, width, top, remove_end):
		outer_pos=0 if top else self.z
		inner_pos=self.material_width if top else self.z-self.material_width
		
		tstart=self.material_width
		tpositions=self.get_tongue_positions(width-2*tstart)
		
		tongues=[
				l(self.material_width if remove_end else 0,inner_pos)
			]+list(itertools.chain(*([[
				l(tstart+tpos[0],inner_pos),
				l(tstart+tpos[0],outer_pos),
				l(tstart+tpos[1],outer_pos),
				l(tstart+tpos[1],inner_pos)]
				for tpos in tpositions
			])))+[
				l(width - (self.material_width if remove_end else 0), inner_pos)
			]
		return tongues if top else tongues[::-1]
	
	def side13(self):
		my_width=self.width-2*self.margin
		
		outlines=Group()
		
		# outlines
		outlines.objects.append(Path("cut",
			[m(0,self.material_width)]+
			self.make_tongues(my_width, True, False)+
			self.make_tongues(my_width, False, False)
		,closed=True))
		
		return (outlines,Group(transformation=(self.material_width,self.material_width)))
	
	def side24(self):
		my_width=self.height-2*self.margin
		
		outlines=Group()
		
		# outlines
		outlines.objects.append(Path("cut",
			[m(self.material_width,self.material_width)]+
			self.make_tongues(my_width, True, True)+
			self.make_tongues(my_width, False, True)
		,closed=True))
		
		return (outlines,Group(transformation=(self.material_width,self.material_width)))

if __name__=="__main__":
	casing=Casing(100,60,30)
	
	sides=[
		("top",casing.top),
		("side13",casing.side13),
		("side24",casing.side24)
		]
	
	
	for name,func in sides:
		svg=SVG((100,60),"casing")
		
		outlines,subview=func()
		outlines.objects.append(subview)
		svg.children.append(outlines)
		
		# test rectangle
		#subview.objects.append(Rectangle(style_cut, (0,0), (10,10)))
	
		with open("cut_{}.svg".format(name),"w") as f:
			f.write(svg.get_svg())