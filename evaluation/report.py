# -*- coding: utf-8 -*-
"""
Visual video tracker evaluator 
    report.py
    Generate report of the evaluation. 
    Formats currently available:
        Latex

@authors: 
    E Daniel Bravo S
    Frances Ryan
"""


def create_report(header, data, metrics):
    """Function creating  Latex report of analysis if selected by user
    
    Args:
        
        header(string): title for report
        data(dictionary): output data from calculation of metrics
        metrics(list): metrics selection from user
    """
    # Importing these libraries here so that these are 'optional' dependencies only required if user 
    # wants to use these functionalities
    from pylatex import Document, Section, Command, LongTabu, Figure, SubFigure, NoEscape
    from pylatex.utils import bold
    
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
                        if 'Precision(Center Location Error)' in metrics:
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

