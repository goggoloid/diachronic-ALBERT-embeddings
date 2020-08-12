import pickle


genre_list = [('financial reporting manual',),
              ('regulatory impact assessment',),
              ('equality impact assessment',),
              ('freedom of information', 'FoI', 'foi'),
              ('evidence assessment',),
              ('economic estimates',),
              ('role specification',),
              ('export of objects',),
              ('call for evidence',),
              ('funding agreement',),
              ('impact assessment',),
              ('technical report',),
              ('spending review',),
              ('tailored review',),
              ('annual report',),
              ('market impact',),
              ('green paper',),
              ('white paper',),
              ('consultation',),
              ('guidance',),
              ('letter',),
              ('strategy',),
              ('survey',),
              ('evaluation',),
              ('review',),
              ('minutes',),
              ('budget',),
              ('act',)]

forbidden = {}
for genre in genre_list:

    if genre[0] == 'act':

        forbidden[genre[0]] = ['action', 'action'.upper(), 'action'.capitalize(),
                               'activity', 'activity'.upper(), 'activity'.capitalize(),
                               'activities', 'activities'.upper(), 'activities'.capitalize(),
                               'contract', 'contract'.upper(), 'contract'.capitalize(),
                               'fact', 'fact'.upper(), 'fact'.capitalize(),
                               'impact', 'impact'.upper(), 'impact'.capitalize(),
                               'practice', 'practice'.upper(), 'practice'.capitalize(),
                               'practioner', 'practioner'.upper(), 'practioner'.capitalize()]

    elif genre[0] == 'survey':

        forbidden[genre[0]] = ['surveyor', 'surveyor'.upper(), 'surveyor'.capitalize(),
                               'surveying', 'surveying'.upper(), 'surveying'.capitalize()]

    else:

        forbidden[genre[0]] = []

pickle.dump(forbidden, open('forbidden.pickle', 'wb'))
pickle.dump(genre_list, open('genre_list.pickle', 'wb'))
