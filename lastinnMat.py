from mat4py import loadmat
import numpy

filepath = "D:/Bakkelår/5 ANNOTATIONS/"
SUBSET_ANNOTATIONS = "1 GUI data/"
DATASET = loadmat(filepath + SUBSET_ANNOTATIONS + "metadata.mat").get("metadata")
fs = 250

def getList(case, variable):
    caseNumber = DATASET["reg_name"].index(case)
    return DATASET[variable][caseNumber]

def getValue(case, variable):
    caseNumber = DATASET["reg_name"].index(case)
    return DATASET[variable][caseNumber]
"""
def plotQRS(case):
    t_qrs = getList(case, "t_qrs")
    i_qrs = list()
    for i in range(len(t_qrs)):
        i_qrs.append(list(t_qrs[i][j] for j in [0, 2]))
        t_qrs[i] = t_qrs[i][1]
    #Sjekk om lista er tom. Spør hva dette er til.
    if not i_qrs:
        #TODO legg til NaN eller ignorer.
    else:
        #Verdt å merke seg at vi her også må bruke handles.s_ecg for signal for y-akse.
        #graphDot(x=t_qrs, y=s_ecg[int(round(t_qrs*handles.fs)+1)])
        #TODO plott inn rektangler ved bruk av i_qrs og sirkler ved bruk av t_qrs

def plotVent(case):
    t_vent = getList(case, "t_vent")
    i_vent = list()
    for i in range(len(t_vent)):
        i_vent.append(list(t_vent[i][j] for j in [0, 2]))
        i_vent[i] = t_vent[i][1]
    #Sjekk om lista er tom. Spør hva dette er til.
    if not i_vent:
        #TODO legg til NaN eller ignorer.
    else:
        #Verdt å merke seg at vi her også må bruke handles.s_vent for signal for y-akse.
        #graphDot(x=t_vent, y=s_vent[int(round(t_vent*handles.fs)+1)])
        #TODO plott inn rektangler ved bruk av i_qrs og sirkler ved bruk av t_qrs
"""
#OK, verdiene i funksjonen under stemmer overens med MATLAB sine.
def plotCOPoints(case):
    t_cap = getList(case, "t_cap")
    t_CO2 = getValue(case, "t_CO2")
    n_min = []
    n_max = []
    t_min = []
    t_max = []
    for item in t_cap:
        n_min.append(int(round(item[0]*fs)) + 1)
        t_min.append(item[0] + t_CO2)
        n_max.append(int(round(item[1]*fs)) + 1)
        t_max.append(item[1] + t_CO2)

    #TODO plott inn min og maks punkter på graf.
    #graphDot(x=t_min, y=s_CO2(n_min))
    #graphDot(x=t_max, y=s_CO2(n_max))

plotCOPoints("CASE_01")


"""
t_vent = getList("CASE_11", "t_vent")
i_vent = list()

for i in range(len(t_vent)):
    i_vent.append(list(t_vent[i][j] for j in [0, 2]))
    t_vent[i] = t_vent[i][1]
for i in i_vent:
    print(i)
for i in t_vent:
    print(i)

"""
