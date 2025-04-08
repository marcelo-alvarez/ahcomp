import numpy as np
from math import log10, floor
round_to_n = lambda x, n: x if x == 0 else round(x, -int(floor(log10(abs(x)))) + (n - 1))

def parsecommmandline(commandline_params):
    import argparse
    parser   = argparse.ArgumentParser()
    for param in commandline_params:
        pval  = commandline_params[param]['val']
        ptype = commandline_params[param]['type']
        pdesc = commandline_params[param]['desc']
        if ptype is bool:
            action='store_true'
            if pval:
                print("storing false")
                action='store_false' 
            parser.add_argument('--'+param, action=action,help=f'{pdesc}')
        else:
            parser.add_argument('--'+param, default=pval, help=f'{pdesc} [{pval}]',type=ptype)
    return vars(parser.parse_args())

commandline_params = {
      'params' : {'val'  : "ombh2,omch2,w0,ns,ln10As,H0,Neff",
                       'type' : str,
                       'desc' : 'comma separated parameter list'},
      'fiducial' : {'val'  : "mdpl2",
                       'type' : str,
                       'desc' : 'fiducial cosmology, either mdpl2 or pl2018'},
      'usemean'  : {'val' : False,
                       'type' : bool,
                       'desc' : 'enable using mean with uncertainties from fiducial'}
           }

fiducials = {
    # https://arxiv.org/pdf/1807.06209
    # Table 4 3rd and 7th rows, last column
    # Table 5 6th row
    'pl2018': {
      'ombh2':  [0.02224, 0.00022],
      'omch2':  [ 0.1179, 0.0028],
      'w0':     [  -1.04, 0.1],
      'ns':     [ 0.9589, 0.0084],
      'ln10As': [  3.036, 0.017],
      'H0':     [   66.3, 1.4],
      'Neff':   [   2.99, 0.34]
    },
    # https://www.cosmosim.org/metadata/mdpl2/
    # https://arxiv.org/pdf/1303.5076
    # Table 2 and eq 74
    'mdpl2': {
      'ombh2':  [0.02214, 0.00033],
      'omch2':  [ 0.1189, 0.003],
      'w0':     [   -1.0, 0.1],
      'ns':     [   0.96, 0.0073],
      'ln10As': [  3.098, 0.057],
      'H0':     [  67.77, 1.5],
      'Neff':   [  3.046, 0.66]     
    }
}

clparams = parsecommmandline(commandline_params)

fiducial = fiducials[clparams['fiducial']]

boxparamsfile = './LH_np7_n25_s555.dat'
boxparams     = np.genfromtxt(boxparamsfile,names=True)
nbox = np.shape(boxparams)[0]
used_params = clparams['params'].split(",")
nused = len(used_params)
usemean = clparams['usemean']

centers = {}
sigmas  = {}
mode_descriptor="values and uncertainties from"
for uparam in used_params:
    centers[uparam] = fiducial[uparam][0]
    sigmas[uparam] = fiducial[uparam][1]
if usemean:
    mode_descriptor="values from mean of boxes (in parentheses) and uncertainties from"
    for uparam in used_params:
        centers[uparam] = boxparams[uparam][:].mean()

boxrms = []
for box in range(nbox):
    l2 = 0.0
    for uparam in used_params:
        cp = centers[uparam]
        sp = sigmas[uparam]
        bp = boxparams[uparam][box]
        dl2 = ((cp-bp)/sp)**2
        l2 += dl2
    l2 /= nused
    boxrms.append(l2**0.5)
boxrms = np.asarray(boxrms)
boxlist = np.argsort(boxrms)

print(f"# using {mode_descriptor} fiducial cosmology {clparams['fiducial']}:")
print(f"#")
for uparam in used_params:
    fp = str(round_to_n(fiducial[uparam][0],4))
    dp = str(fiducial[uparam][1])
    if usemean:
        cp = str(round_to_n(centers[uparam],4))
        print(f"#  {uparam:>6}: {fp:>7} ({cp:>7}) +/- {dp:>7}")
    else:
        print(f"#  {uparam:>6}: {fp:>7} +/- {dp:>7}")
print(f"#")
print(f"# column 1: box")
print(f"# column 2: rms distance from fiducial")
for uparam in range(len(used_params)):
    print(f"# column {uparam+3}: {used_params[uparam]}")
print(f"")
for box in boxlist:
    pvals = []
    for uparam in used_params:
        pvals.append((str(boxparams[uparam][box])).rjust(10))
    print(f"{box:>2} {boxrms[box]:.3f} {" ".join(pvals)}")
