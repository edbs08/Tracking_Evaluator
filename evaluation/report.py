# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 14:09:18 2019

@author: Frances
"""

from pylatex import Document, Section, Subsection, Command, LongTabu, Tabu, Center, Figure, SubFigure, NoEscape, LineBreak, UnsafeCommand
from pylatex.utils import bold

def create_report(header, data, metrics):
    challenges = data.keys()
    
    geometry_options = {
        "margin": "1.5in",
        "headheight": "20pt",
        "headsep": "10pt",
        "includeheadfoot": True
    }
    doc = Document(header, page_numbers=True, geometry_options=geometry_options)
    
    with doc.create(Section('Tables')):
            fmt = "X[r] X[r]"
            for i in range(len(metrics)):
                fmt += " X[r]"
                
            with doc.create(LongTabu(fmt, spread="1.5pt")) as data_table:
                header_row1 = ["Challenge", "Tracker"]
                for m in metrics:
                    header_row1.append(m)

                data_table.add_row(header_row1, mapper=[bold])
                for c in challenges:
                    data_table.add_hline()
                    row = [c, ' ']
                    for i in range(len(metrics)):
                        row.append(' ')
                    data_table.add_row(row)
                    data_table.add_hline()
                    for t in data[c].keys():
                        row = [' ', t]
                        if 'Accuracy' in metrics:
                            row.append(data[c][t]['tracker_acc'])
                        if 'Robustness' in metrics:
                            row.append(data[c][t]['tracker_robust'])
                        if 'Precision' in metrics:
                            row.append(data[c][t]['tracker_precision'])
                        data_table.add_row(row)
    
    if 'Accuracy' and 'Robustness' in metrics:
        doc.append(Command('newpage'))
        with doc.create(Section('AR-Plots')):
            width = 2/(len(challenges))
            width_str = str(width) + '\linewidth'
            with doc.create(Figure(position='h!')) as plots:
                for c in challenges:
                    with doc.create(SubFigure(width=NoEscape(r'%s'%width_str))) as subfig:
                        image_filename = 'AR_%s.png'%c
                        subfig.add_image(image_filename, width=NoEscape(r'\linewidth'))
                        subfig.add_caption('%s'%c)
                    doc.append(Command('hfill'))
                plots.add_caption('Accuracy-Robustness')
            
        
            
    doc.generate_tex()
