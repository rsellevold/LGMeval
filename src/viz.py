class viz:

    def __init__(self):
        self.fontsize = 12

        self.maintitle = None
        self.lefttitle = None
        self.righttitle = None
        
    
    def titles(self, ax):
        if self.maintitle is not None:
            if lefttitle is not None or righttitle is not None:
                ax.set_title(self.maintitle, fontsize=self.fontsize, y=1.12)
            else:
                ax.set_title(self.maintitle, fontsize=self.fontsize, y=1.04)
                
        if self.lefttile is not None:
            ax.set_title(self.lefttitle, fontsize=self.fontsize-2, loc="left")
        if self.righttitle is not None:
            ax.set_title(self.righttitle, fontsize=self.fontsize-2, loc="right")
