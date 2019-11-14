def Gen_data_to_mapping(arg_list):
    keys = ['name', 'a', 'b', 'c','Pmax', 'Pmin']
    dic = {}
    for i in range(len(arg_list)):
        dic[keys[i]] = arg_list[i]
    return dic

demand_sep = 700

def generators():
    data = [['G1',0.00048,16.19,1000,455,150],
            ['G2',0.00031,17.26,970,455,150],
            ['G3',0.00200,16.6,700,130,20],
            ['G4',0.00211,16.5,680,130,20],
    ]
    g = {}
    for i in range(len(data)):
        g[i] = Gen_data_to_mapping(data[i])
    return g