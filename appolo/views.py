from django.http import HttpResponse
from django.shortcuts import render
import pprint
import json

from appolo.models import Locatie, Nieuwsitem, Dag, Activiteit
from zues.models import Organimo, PolitiekeMotie, ActuelePolitiekeMotie, Resolutie, Amendement, HRWijziging, Stuk

def locaties():
    locatieList = [x for x in Locatie.objects.values()]
    return locatieList

def nieuwsitems():
    nieuwsList = [x for x in Nieuwsitem.objects.values()]
    return nieuwsList

def agenda():
    agendaList = Dag.objects.all()
    allActiviteiten = []
    for dag in agendaList:
        dagEntry = {
            'datum': dag.__dict__['datum'].isoformat(), 
            'items': []
        }
        activiteitenList = dag.activiteit_set.all()
        for activiteit in activiteitenList:
            activiteitEntry = {
                'tijd': activiteit.__dict__['begintijd'].isoformat(),
                'eindtijd': activiteit.__dict__['eindtijd'].isoformat(),
                'titel': activiteit.__dict__['naam'],
                'locatie': activiteit.locatie.__dict__['naam'] 
            }
            dagEntry['items'].append(activiteitEntry)
        allActiviteiten.append(dagEntry)
    return allActiviteiten

def data(request):
    dataDict = {}
    dataDict['nieuwsitems'] = nieuwsitems()
    dataDict['agenda'] = agenda()
    dataDict['locaties'] = locaties()
    voorstellen = {}
    voorstellen['Politieke Moties'] = [x.as_dict() for x in PolitiekeMotie.objects.filter(status=Stuk.PUBLIEK)]
    voorstellen["Organimo's"] = [x.as_dict() for x in Organimo.objects.filter(status=Stuk.PUBLIEK)]
    voorstellen['Actuele Politieke Moties'] = [x.as_dict() for x in ActuelePolitiekeMotie.objects.filter(status=Stuk.PUBLIEK)]
    voorstellen['Resoluties'] = [x.as_dict() for x in Resolutie.objects.filter(status=Stuk.PUBLIEK)]
    voorstellen['Amendementen'] = [x.as_dict() for x in Amendement.objects.filter(status=Stuk.PUBLIEK)]
    voorstellen['HR-wijzigingen'] = [x.as_dict() for x in HRWijziging.objects.filter(status=Stuk.PUBLIEK)]
    dataDict['voorstellen'] = voorstellen
    output = json.dumps(dataDict, indent=4, separators=(',', ': '))
    return HttpResponse(output)
