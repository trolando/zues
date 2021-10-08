from django.http import HttpResponse
import json

from appolo.models import Locatie, Nieuwsitem, Dag
from zues.models import Organimo, PolitiekeMotie, ActuelePolitiekeMotie, Resolutie, Amendement, HRWijziging, Stuk


def locaties():

    locatie_list = [x for x in Locatie.objects.values()]
    return locatie_list


def nieuwsitems():
    nieuws_list = [x for x in Nieuwsitem.objects.values()]
    return nieuws_list


def agenda():
    agenda_list = Dag.objects.all()
    all_activiteiten = []
    for dag in agenda_list:
        dag_entry = {
            'datum': dag.__dict__['datum'].isoformat(), 
            'items': []
        }
        activiteiten_list = dag.activiteit_set.all()
        for activiteit in activiteiten_list:
            activiteit_entry = {
                'tijd': activiteit.__dict__['begintijd'].isoformat(),
                'eindtijd': activiteit.__dict__['eindtijd'].isoformat(),
                'titel': activiteit.__dict__['naam'],
                'locatie': activiteit.locatie.__dict__['naam'] 
            }
            dag_entry['items'].append(activiteit_entry)
        all_activiteiten.append(dag_entry)
    return all_activiteiten


def data(request):
    data_dict = {'nieuwsitems': nieuwsitems(), 'agenda': agenda(), 'locaties': locaties()}
    voorstellen = {}
    # het aantal politieke moties loopt soms over de 100,
    # en dan is er een extra voorloopnul nodig in het nummer (e.g. PM052)
    li = PolitiekeMotie.objects.filter(status=Stuk.PUBLIEK)
    boeknrlen = len(str(len(li)))
    voorstellen['Politieke Moties'] = [x.as_dict(boeknrlen) for x in li]
    voorstellen["Organimo's"] = [x.as_dict() for x in Organimo.objects.filter(status=Stuk.PUBLIEK)]
    voorstellen['Actuele Politieke Moties'] = \
        [x.as_dict() for x in ActuelePolitiekeMotie.objects.filter(status=Stuk.PUBLIEK)]
    voorstellen['Resoluties'] = [x.as_dict() for x in Resolutie.objects.filter(status=Stuk.PUBLIEK)]
    voorstellen['Amendementen'] = [x.as_dict() for x in Amendement.objects.filter(status=Stuk.PUBLIEK)]
    voorstellen['HR-wijzigingen'] = [x.as_dict() for x in HRWijziging.objects.filter(status=Stuk.PUBLIEK)]
    data_dict['voorstellen'] = voorstellen
    output = json.dumps(data_dict, ensure_ascii=False, indent=4, separators=(',', ': '))
    return HttpResponse(output)
